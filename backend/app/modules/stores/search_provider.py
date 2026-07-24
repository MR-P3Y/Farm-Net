from decimal import Decimal

from app.common.search import (
    SearchProvider,
    SearchResultType,
    SearchSort,
    UnifiedSearchGroup,
    UnifiedSearchQuery,
    UnifiedSearchResult,
    search_relevance_score,
)
from app.modules.stores.enums import StoreDiscoverySort
from app.modules.stores.repository import StoreRepository
from app.modules.reviews.repository import ReviewsRepository


class StoreSearchProvider(SearchProvider):
    result_type = SearchResultType.STORE

    def __init__(
        self,
        db,
        repository: StoreRepository | None = None,
        ratings_repository: ReviewsRepository | None = None,
    ) -> None:
        self.repo = repository or StoreRepository(db)
        self.ratings = ratings_repository or ReviewsRepository(db)

    def search(self, query: UnifiedSearchQuery) -> UnifiedSearchGroup:
        sort = (
            StoreDiscoverySort.NEWEST
            if query.sort == SearchSort.NEWEST
            else StoreDiscoverySort.RELEVANCE
        )
        filters = query.filters
        rows, total = self.repo.list_public_stores(
            q=query.q,
            province_id=filters.province_id,
            city_id=filters.city_id,
            sort=sort,
            page=query.page,
            page_size=query.page_size,
        )
        ratings = self.ratings.rating_values_by_subject_ids(
            subject_type="store",
            subject_ids=[row.id for row in rows],
        )
        items = []
        for row in rows:
            rating, _ = ratings.get(row.id, (Decimal("0.00"), 0))
            items.append(
                UnifiedSearchResult(
                    type=self.result_type,
                    resource_id=row.id,
                    title=row.name,
                    subtitle=row.description[:500] if row.description else None,
                    route=f"/stores/{row.slug}",
                    province_id=row.province_id,
                    city_id=row.city_id,
                    rating=rating,
                    relevance_score=search_relevance_score(
                        query.q, row.name, row.slug, row.description
                    ),
                )
            )
        return UnifiedSearchGroup(
            type=self.result_type,
            items=items,
            total=total,
            page=query.page,
            page_size=query.page_size,
        )
