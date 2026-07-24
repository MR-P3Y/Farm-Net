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
from app.modules.rentals.enums import RentalDiscoverySort
from app.modules.rentals.repository import RentalRepository
from app.modules.reviews.repository import ReviewsRepository


class RentalSearchProvider(SearchProvider):
    result_type = SearchResultType.RENTAL_EQUIPMENT

    def __init__(
        self,
        db,
        repository: RentalRepository | None = None,
        ratings_repository: ReviewsRepository | None = None,
    ) -> None:
        self.repo = repository or RentalRepository(db)
        self.ratings = ratings_repository or ReviewsRepository(db)

    def search(self, query: UnifiedSearchQuery) -> UnifiedSearchGroup:
        sort = {
            SearchSort.NEWEST: RentalDiscoverySort.NEWEST,
            SearchSort.PRICE_ASC: RentalDiscoverySort.PRICE_ASC,
            SearchSort.PRICE_DESC: RentalDiscoverySort.PRICE_DESC,
        }.get(query.sort, RentalDiscoverySort.RELEVANCE)
        filters = query.filters
        rows, total = self.repo.list_equipment(
            public=True,
            q=query.q,
            category_id=filters.rental_category_id,
            province_id=filters.province_id,
            city_id=filters.city_id,
            operator_mode=filters.rental_operator_mode,
            min_price=filters.min_price,
            max_price=filters.max_price,
            available_from=filters.rental_available_from,
            available_to=filters.rental_available_to,
            sort=sort,
            page=query.page,
            page_size=query.page_size,
        )
        ratings = self.ratings.rating_values_by_subject_ids(
            subject_type="rental_equipment",
            subject_ids=[row.id for row in rows],
        )
        items = []
        for row in rows:
            active_prices = [
                price
                for price in row.pricing_rules
                if price.is_active and price.currency == "TOMAN"
            ]
            minimum_price = min(active_prices, key=lambda price: price.price_amount, default=None)
            rating, _ = ratings.get(row.id, (Decimal("0.00"), 0))
            items.append(
                UnifiedSearchResult(
                    type=self.result_type,
                    resource_id=row.id,
                    title=row.title,
                    subtitle=row.description[:500]
                    if row.description
                    else row.lessor_profile.display_name,
                    route=f"/rentals/equipment/{row.id}",
                    province_id=row.province_id,
                    city_id=row.city_id,
                    price=minimum_price.price_amount if minimum_price else None,
                    currency=minimum_price.currency if minimum_price else None,
                    rating=rating,
                    relevance_score=search_relevance_score(
                        query.q,
                        row.title,
                        row.slug,
                        row.description,
                        row.manufacturer,
                        row.model_name,
                        row.lessor_profile.display_name,
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
