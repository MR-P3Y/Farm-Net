import hashlib
import json
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.modules.ai.models import AIContextConsent
from app.modules.ai.schemas import AIContextConsentCreateIn
from app.modules.auth.models import AuthUser
from app.modules.farms.models import Farm, FarmCropCycle, FarmPlot


CONSENT_VERSION = "barzegar-farm-context-v1"


class AIContextService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_consent(
        self, *, user: AuthUser, payload: AIContextConsentCreateIn
    ) -> AIContextConsent:
        farm, plot, cycle = self._owned_selection(
            user_id=user.id,
            farm_id=payload.farm_id,
            plot_id=payload.plot_id,
            crop_cycle_id=payload.crop_cycle_id,
        )
        fingerprint = self._selection_fingerprint(
            user_id=user.id,
            farm_id=farm.id,
            plot_id=plot.id if plot else None,
            crop_cycle_id=cycle.id if cycle else None,
            purpose=payload.purpose,
        )
        existing = self.db.scalar(
            select(AIContextConsent).where(
                AIContextConsent.user_id == user.id,
                AIContextConsent.idempotency_key == payload.idempotency_key,
            )
        )
        if existing is not None:
            if existing.selection_fingerprint != fingerprint:
                raise AppException(
                    "AI_CONSENT_IDEMPOTENCY_CONFLICT",
                    "Consent idempotency key was used for another selection",
                    409,
                )
            return existing

        self._expire_consents(user_id=user.id)
        active = self.db.scalar(
            select(AIContextConsent).where(
                AIContextConsent.active_scope == fingerprint,
                AIContextConsent.status == "active",
            )
        )
        if active is not None:
            return active

        now = datetime.utcnow()
        row = AIContextConsent(
            user_id=user.id,
            farm_id=farm.id,
            plot_id=plot.id if plot else None,
            crop_cycle_id=cycle.id if cycle else None,
            idempotency_key=payload.idempotency_key,
            selection_fingerprint=fingerprint,
            active_scope=fingerprint,
            purpose=payload.purpose,
            consent_version=CONSENT_VERSION,
            status="active",
            granted_at=now,
            expires_at=now + timedelta(hours=payload.expires_in_hours),
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def list_consents(self, *, user: AuthUser) -> list[AIContextConsent]:
        self._expire_consents(user_id=user.id)
        return list(
            self.db.scalars(
                select(AIContextConsent)
                .where(AIContextConsent.user_id == user.id)
                .order_by(AIContextConsent.granted_at.desc(), AIContextConsent.id.desc())
            )
        )

    def revoke(self, *, user: AuthUser, consent_id: int, reason: str) -> AIContextConsent:
        row = self.db.scalar(
            select(AIContextConsent)
            .where(
                AIContextConsent.id == consent_id,
                AIContextConsent.user_id == user.id,
            )
            .with_for_update()
        )
        if row is None:
            raise AppException("AI_CONTEXT_CONSENT_NOT_FOUND", "Consent not found", 404)
        if row.status != "active":
            return row
        row.status = "revoked"
        row.active_scope = None
        row.revoked_at = datetime.utcnow()
        row.revocation_reason = reason.strip()
        self.db.commit()
        self.db.refresh(row)
        return row

    def capture_manifest(
        self,
        *,
        user_id: int,
        consent_id: int,
        request_kind: str,
    ) -> tuple[AIContextConsent, dict, datetime]:
        now = datetime.utcnow()
        consent = self.db.scalar(
            select(AIContextConsent)
            .where(
                AIContextConsent.id == consent_id,
                AIContextConsent.user_id == user_id,
            )
            .with_for_update()
        )
        if consent is None:
            raise AppException("AI_CONTEXT_CONSENT_NOT_FOUND", "Consent not found", 404)
        if (
            consent.status != "active"
            or consent.expires_at is not None
            and consent.expires_at <= now
        ):
            if consent.status == "active":
                consent.status = "expired"
                consent.active_scope = None
            raise AppException(
                "AI_CONTEXT_CONSENT_INACTIVE",
                "Selected Farm context consent is not active",
                409,
            )
        expected_purpose = {
            "text": "answer_question",
            "farm_context": "answer_question",
            "deep_analysis": "deep_analysis",
            "image_analysis": "image_analysis",
            "smart_diary": "smart_diary",
            "report": "report",
        }[request_kind]
        if consent.purpose != expected_purpose:
            raise AppException(
                "AI_CONTEXT_PURPOSE_MISMATCH",
                "Consent purpose does not match the request",
                409,
            )
        farm, plot, cycle = self._owned_selection(
            user_id=user_id,
            farm_id=consent.farm_id,
            plot_id=consent.plot_id,
            crop_cycle_id=consent.crop_cycle_id,
        )
        manifest = {
            "schema_version": CONSENT_VERSION,
            "consent_id": consent.id,
            "consent_version": consent.consent_version,
            "purpose": consent.purpose,
            "farm": {
                "id": farm.id,
                "name": farm.name,
                "status": farm.status,
                "declared_area_sqm": (
                    str(farm.declared_area_sqm) if farm.declared_area_sqm is not None else None
                ),
                "updated_at": farm.updated_at.isoformat(),
            },
            "plot": (
                {
                    "id": plot.id,
                    "name": plot.name,
                    "status": plot.status,
                    "area_sqm": str(plot.area_sqm),
                    "province_id": plot.province_id,
                    "city_id": plot.city_id,
                    "updated_at": plot.updated_at.isoformat(),
                }
                if plot
                else None
            ),
            "crop_cycle": (
                {
                    "id": cycle.id,
                    "crop_id": cycle.crop_id,
                    "variety_id": cycle.variety_id,
                    "title": cycle.title,
                    "status": cycle.status,
                    "planned_start_date": cycle.planned_start_date.isoformat(),
                    "planned_end_date": cycle.planned_end_date.isoformat(),
                    "updated_at": cycle.updated_at.isoformat(),
                }
                if cycle
                else None
            ),
        }
        manifest["freshness_sha256"] = hashlib.sha256(
            json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        return consent, manifest, now

    def is_manifest_fresh(self, *, request_context: dict, user_id: int) -> bool:
        try:
            consent_id = int(request_context["consent_id"])
            consent, current, _ = self.capture_manifest(
                user_id=user_id,
                consent_id=consent_id,
                request_kind=self._purpose_to_request_kind(
                    str(request_context["consent_version"]),
                    str(request_context.get("purpose", "answer_question")),
                ),
            )
        except (AppException, KeyError, TypeError, ValueError):
            return False
        return consent.status == "active" and current["freshness_sha256"] == request_context.get(
            "freshness_sha256"
        )

    def _owned_selection(
        self,
        *,
        user_id: int,
        farm_id: int,
        plot_id: int | None,
        crop_cycle_id: int | None,
    ) -> tuple[Farm, FarmPlot | None, FarmCropCycle | None]:
        farm = self.db.scalar(
            select(Farm).where(
                Farm.id == farm_id,
                Farm.owner_user_id == user_id,
                Farm.status == "active",
            )
        )
        if farm is None:
            raise AppException("AI_FARM_SELECTION_NOT_FOUND", "Farm selection not found", 404)
        plot = None
        if plot_id is not None:
            plot = self.db.scalar(
                select(FarmPlot).where(
                    FarmPlot.id == plot_id,
                    FarmPlot.farm_id == farm.id,
                    FarmPlot.status == "active",
                )
            )
            if plot is None:
                raise AppException("AI_FARM_SELECTION_NOT_FOUND", "Farm selection not found", 404)
        cycle = None
        if crop_cycle_id is not None:
            if plot is None:
                raise AppException(
                    "AI_FARM_SELECTION_INVALID",
                    "Crop cycle selection requires its plot",
                    422,
                )
            cycle = self.db.scalar(
                select(FarmCropCycle).where(
                    FarmCropCycle.id == crop_cycle_id,
                    FarmCropCycle.plot_id == plot.id,
                    FarmCropCycle.status != "cancelled",
                )
            )
            if cycle is None:
                raise AppException("AI_FARM_SELECTION_NOT_FOUND", "Farm selection not found", 404)
        return farm, plot, cycle

    def _expire_consents(self, *, user_id: int) -> None:
        now = datetime.utcnow()
        rows = self.db.scalars(
            select(AIContextConsent).where(
                AIContextConsent.user_id == user_id,
                AIContextConsent.status == "active",
                AIContextConsent.expires_at <= now,
            )
        )
        changed = False
        for row in rows:
            row.status = "expired"
            row.active_scope = None
            changed = True
        if changed:
            self.db.commit()

    @staticmethod
    def _selection_fingerprint(
        *,
        user_id: int,
        farm_id: int,
        plot_id: int | None,
        crop_cycle_id: int | None,
        purpose: str,
    ) -> str:
        value = f"{user_id}:{farm_id}:{plot_id}:{crop_cycle_id}:{purpose}:{CONSENT_VERSION}"
        return hashlib.sha256(value.encode()).hexdigest()

    @staticmethod
    def _purpose_to_request_kind(consent_version: str, purpose: str) -> str:
        if consent_version != CONSENT_VERSION:
            raise ValueError("Unsupported consent version")
        return {
            "answer_question": "text",
            "deep_analysis": "deep_analysis",
            "image_analysis": "image_analysis",
            "smart_diary": "smart_diary",
            "report": "report",
        }[purpose]
