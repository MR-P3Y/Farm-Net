from app.common.search import (
    SearchProvider,
    SearchResultType,
    SearchSort,
    UnifiedSearchGroup,
    UnifiedSearchQuery,
    UnifiedSearchResult,
    search_relevance_score,
)
from app.modules.products.enums import ProductDiscoverySort
from app.modules.products.repository import ProductRepository


class ProductSearchProvider(SearchProvider):
    result_type = SearchResultType.PRODUCT

    def __init__(self, db, repository: ProductRepository | None = None) -> None:
        self.repo = repository or ProductRepository(db)

    def search(self, query: UnifiedSearchQuery) -> UnifiedSearchGroup:
        sort = {
            SearchSort.NEWEST: ProductDiscoverySort.NEWEST,
            SearchSort.PRICE_ASC: ProductDiscoverySort.PRICE_ASC,
            SearchSort.PRICE_DESC: ProductDiscoverySort.PRICE_DESC,
        }.get(query.sort, ProductDiscoverySort.RELEVANCE)
        filters = query.filters
        rows, total = self.repo.list_public_products(
            q=query.q,
            category_id=filters.product_category_id,
            province_id=filters.province_id,
            city_id=filters.city_id,
            min_price=filters.min_price,
            max_price=filters.max_price,
            sort=sort,
            page=query.page,
            page_size=query.page_size,
        )
        items = [
            UnifiedSearchResult(
                type=self.result_type,
                resource_id=row.id,
                title=row.name,
                subtitle=row.short_description or getattr(row.store, "name", None),
                route=f"/products/{row.id}",
                province_id=getattr(row.store, "province_id", None),
                city_id=getattr(row.store, "city_id", None),
                price=row.price,
                currency=row.currency,
                relevance_score=search_relevance_score(
                    query.q,
                    row.name,
                    row.slug,
                    row.short_description,
                    row.description,
                    getattr(row.store, "name", None),
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
