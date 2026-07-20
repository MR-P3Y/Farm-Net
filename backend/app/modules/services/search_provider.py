from app.common.search import (
    SearchProvider,
    SearchResultType,
    SearchSort,
    UnifiedSearchGroup,
    UnifiedSearchQuery,
    UnifiedSearchResult,
    search_relevance_score,
)
from app.modules.services.enums import ServiceDiscoverySort
from app.modules.services.repository import ServicesRepository


class ServiceSearchProvider(SearchProvider):
    result_type = SearchResultType.SERVICE

    def __init__(self, db, repository: ServicesRepository | None = None) -> None:
        self.repo = repository or ServicesRepository(db)

    def search(self, query: UnifiedSearchQuery) -> UnifiedSearchGroup:
        sort = {
            SearchSort.NEWEST: ServiceDiscoverySort.NEWEST,
            SearchSort.PRICE_ASC: ServiceDiscoverySort.PRICE_ASC,
            SearchSort.PRICE_DESC: ServiceDiscoverySort.PRICE_DESC,
            SearchSort.RATING: ServiceDiscoverySort.RATING,
        }.get(query.sort, ServiceDiscoverySort.RELEVANCE)
        filters = query.filters
        rows, total = self.repo.list_public_offers(
            q=query.q,
            category_id=filters.service_category_id,
            provider_profile_id=None,
            pricing_type=filters.service_pricing_type,
            province_id=filters.province_id,
            city_id=filters.city_id,
            min_price=filters.min_price,
            max_price=filters.max_price,
            sort=sort,
            page=query.page,
            page_size=query.page_size,
        )
        items = []
        for row in rows:
            provider = row.provider_profile
            secondary = row.short_description or provider.display_name or provider.title
            items.append(
                UnifiedSearchResult(
                    type=self.result_type,
                    resource_id=row.id,
                    title=row.title,
                    subtitle=secondary,
                    route=f"/services/{row.id}",
                    province_id=row.province_id,
                    city_id=row.city_id,
                    price=row.price_amount,
                    currency=row.currency if row.price_amount is not None else None,
                    rating=provider.rating_average,
                    relevance_score=search_relevance_score(
                        query.q,
                        row.title,
                        row.slug,
                        row.short_description,
                        row.description,
                        row.service_area,
                        provider.display_name,
                        provider.title,
                        row.category.title if row.category else None,
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
