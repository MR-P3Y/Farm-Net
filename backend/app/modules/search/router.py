from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.common.search import UnifiedSearchEngine, UnifiedSearchQuery
from app.core.responses import success_response
from app.db.session import get_db
from app.modules.consultants.search_provider import ConsultantSearchProvider
from app.modules.products.search_provider import ProductSearchProvider
from app.modules.rentals.search_provider import RentalSearchProvider
from app.modules.services.search_provider import ServiceSearchProvider
from app.modules.social.search_provider import SocialSearchProvider
from app.modules.stores.search_provider import StoreSearchProvider


router = APIRouter(prefix="/search", tags=["Search"])


def build_search_engine(db: Session) -> UnifiedSearchEngine:
    return UnifiedSearchEngine(
        [
            ProductSearchProvider(db),
            StoreSearchProvider(db),
            ServiceSearchProvider(db),
            RentalSearchProvider(db),
            ConsultantSearchProvider(db),
            SocialSearchProvider(db),
        ]
    )


@router.post("")
def unified_search(
    payload: UnifiedSearchQuery,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Robots-Tag"] = "noindex, nofollow"
    result = build_search_engine(db).search(payload)
    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )
