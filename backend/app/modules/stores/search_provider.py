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


class StoreSearchProvider(SearchProvider):
    result_type = SearchResultType.STORE

    def __init__(self, db, repository: StoreRepository | None = None) -> None:
        self.repo = repository or StoreRepository(db)

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
        items = [
            UnifiedSearchResult(
                type=self.result_type,
                resource_id=row.id,
                title=row.name,
                subtitle=row.description[:500] if row.description else None,
                route=f"/stores/{row.slug}",
                province_id=row.province_id,
                city_id=row.city_id,
                relevance_score=search_relevance_score(
                    query.q, row.name, row.slug, row.description
                ),
            )
            for row in rows
        ]
        return UnifiedSearchGroup(
            type=self.result_type,
            items=items,
            total=total,
            page=query.page,
            page_size=query.page_size,
        )
