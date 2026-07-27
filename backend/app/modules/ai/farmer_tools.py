import json
from datetime import datetime

from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.modules.ai.models import AIDiarySuggestion, AIFarmerReport, AIRequest
from app.modules.ai.schemas import (
    AIDiaryDecisionIn,
    AIDiaryOperationProposal,
)
from app.modules.auth.models import AuthUser
from app.modules.farms.diary_service import FarmDiaryService
from app.modules.farms.models import (
    FarmCropCycle,
    FarmHarvestObservation,
    FarmOperation,
    FarmOperationInput,
    FarmPlot,
)
from app.modules.farms.schemas import FarmOperationCreateIn


class AIFarmerToolsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def materialize_success(self, *, request: AIRequest, content: str) -> None:
        if request.request_kind == "smart_diary":
            self._create_diary_suggestion(request=request, content=content)
        elif request.request_kind == "report":
            self._create_report(request=request, content=content)

    def list_suggestions(self, *, user: AuthUser) -> list[AIDiarySuggestion]:
        return list(
            self.db.scalars(
                select(AIDiarySuggestion)
                .where(AIDiarySuggestion.user_id == user.id)
                .order_by(AIDiarySuggestion.created_at.desc(), AIDiarySuggestion.id.desc())
            )
        )

    def decide(
        self, *, user: AuthUser, suggestion_id: int, accept: bool, payload: AIDiaryDecisionIn
    ) -> AIDiarySuggestion:
        row = self.db.scalar(
            select(AIDiarySuggestion)
            .where(
                AIDiarySuggestion.id == suggestion_id,
                AIDiarySuggestion.user_id == user.id,
            )
            .with_for_update()
        )
        if row is None:
            raise AppException("AI_DIARY_SUGGESTION_NOT_FOUND", "Diary suggestion not found", 404)
        if row.status != "pending":
            return row
        now = datetime.utcnow()
        if not accept:
            row.status = "rejected"
            row.rejection_reason = payload.reason
            row.decided_at = now
            self.db.commit()
            self.db.refresh(row)
            return row

        proposal = AIDiaryOperationProposal.model_validate(row.proposed_operation)
        diary = FarmDiaryService(self.db)
        cycle = diary._active_cycle(
            user.id, row.farm_id, row.plot_id, row.crop_cycle_id, True
        )
        operation_payload = FarmOperationCreateIn(
            operation_type=proposal.operation_type,
            title=proposal.title,
            occurred_on=proposal.occurred_on,
            notes=proposal.notes,
        )
        if operation_payload.occurred_on < cycle.actual_start_date:
            raise AppException(
                "FARM_OPERATION_DATE_INVALID",
                "Operation date cannot precede cycle start date",
                422,
            )
        operation = diary.repo.add(
            FarmOperation(
                cycle_id=cycle.id,
                operation_type=operation_payload.operation_type.value,
                title=operation_payload.title,
                occurred_on=operation_payload.occurred_on,
                notes=operation_payload.notes,
            )
        )
        self.db.flush()
        diary.repo.add_audit(
            farm_id=row.farm_id,
            actor_user_id=user.id,
            action="operation.created_from_ai_suggestion",
            target_type="operation",
            target_id=operation.id,
        )
        row.status = "accepted"
        row.farm_operation_id = operation.id
        row.decided_at = now
        self.db.commit()
        self.db.refresh(row)
        return row

    def list_reports(self, *, user: AuthUser) -> list[AIFarmerReport]:
        return list(
            self.db.scalars(
                select(AIFarmerReport)
                .where(AIFarmerReport.user_id == user.id)
                .order_by(AIFarmerReport.generated_at.desc(), AIFarmerReport.id.desc())
            )
        )

    def _create_diary_suggestion(self, *, request: AIRequest, content: str) -> None:
        if self.db.scalar(
            select(AIDiarySuggestion).where(AIDiarySuggestion.request_id == request.id)
        ):
            return
        selection = self._selection(request)
        if selection["plot_id"] is None or selection["crop_cycle_id"] is None:
            raise AppException(
                "AI_DIARY_CONTEXT_INCOMPLETE",
                "Smart diary requires a selected plot and crop cycle",
                422,
            )
        try:
            raw = json.loads(content)
            proposal = AIDiaryOperationProposal.model_validate(raw)
        except (json.JSONDecodeError, ValidationError) as exc:
            raise AppException(
                "AI_DIARY_OUTPUT_INVALID",
                "Smart diary output must match the operation proposal contract",
                422,
            ) from exc
        self.db.add(
            AIDiarySuggestion(
                request_id=request.id,
                user_id=request.user_id,
                farm_id=selection["farm_id"],
                plot_id=selection["plot_id"],
                crop_cycle_id=selection["crop_cycle_id"],
                proposed_operation=proposal.model_dump(mode="json"),
                status="pending",
            )
        )

    def _create_report(self, *, request: AIRequest, content: str) -> None:
        if self.db.scalar(select(AIFarmerReport).where(AIFarmerReport.request_id == request.id)):
            return
        selection = self._selection(request)
        cycle_ids = select(FarmCropCycle.id).join(
            FarmPlot, FarmPlot.id == FarmCropCycle.plot_id
        )
        if selection["crop_cycle_id"] is not None:
            cycle_ids = cycle_ids.where(FarmCropCycle.id == selection["crop_cycle_id"])
        elif selection["plot_id"] is not None:
            cycle_ids = cycle_ids.where(FarmCropCycle.plot_id == selection["plot_id"])
        else:
            cycle_ids = cycle_ids.where(FarmPlot.farm_id == selection["farm_id"])
        operation_count = self.db.scalar(
            select(func.count(FarmOperation.id)).where(FarmOperation.cycle_id.in_(cycle_ids))
        ) or 0
        input_count = self.db.scalar(
            select(func.count(FarmOperationInput.id))
            .join(FarmOperation, FarmOperation.id == FarmOperationInput.operation_id)
            .where(FarmOperation.cycle_id.in_(cycle_ids))
        ) or 0
        harvest_count = self.db.scalar(
            select(func.count(FarmHarvestObservation.id)).where(
                FarmHarvestObservation.cycle_id.in_(cycle_ids)
            )
        ) or 0
        snapshot = {
            **selection,
            "operation_count": operation_count,
            "input_count": input_count,
            "harvest_count": harvest_count,
            "context_freshness_sha256": request.context_manifest["freshness_sha256"],
        }
        self.db.add(
            AIFarmerReport(
                request_id=request.id,
                user_id=request.user_id,
                source_snapshot=snapshot,
                narrative=content.strip(),
                **selection,
            )
        )

    @staticmethod
    def _selection(request: AIRequest) -> dict:
        manifest = request.context_manifest
        if not manifest:
            raise AppException(
                "AI_CONTEXT_REQUIRED",
                "Selected Farm context consent is required",
                422,
            )
        return {
            "farm_id": int(manifest["farm"]["id"]),
            "plot_id": int(manifest["plot"]["id"]) if manifest.get("plot") else None,
            "crop_cycle_id": (
                int(manifest["crop_cycle"]["id"]) if manifest.get("crop_cycle") else None
            ),
        }
