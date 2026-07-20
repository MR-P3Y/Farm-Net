from app.common.search import (
    SearchProvider,
    SearchResultType,
    SearchSort,
    UnifiedSearchGroup,
    UnifiedSearchQuery,
    UnifiedSearchResult,
    search_relevance_score,
)
from app.modules.consultants.enums import ConsultantDiscoverySort
from app.modules.consultants.repository import ConsultantRepository


class ConsultantSearchProvider(SearchProvider):
    result_type = SearchResultType.CONSULTANT

    def __init__(self, db, repository: ConsultantRepository | None = None) -> None:
        self.repo = repository or ConsultantRepository(db)

    def search(self, query: UnifiedSearchQuery) -> UnifiedSearchGroup:
        sort = {
            SearchSort.NEWEST: ConsultantDiscoverySort.NEWEST,
            SearchSort.RATING: ConsultantDiscoverySort.RATING,
        }.get(query.sort, ConsultantDiscoverySort.RELEVANCE)
        filters = query.filters
        rows, total = self.repo.list_profiles(
            public_only=True,
            specialty_id=filters.consultant_specialty_id,
            q=query.q,
            province_id=filters.province_id,
            city_id=filters.city_id,
            sort=sort,
            page=query.page,
            page_size=query.page_size,
        )
        items = []
        for row in rows:
            specialty_text = "، ".join(
                link.specialty.title
                for link in row.specialty_links
                if link.specialty is not None and link.specialty.is_active
            )
            items.append(
                UnifiedSearchResult(
                    type=self.result_type,
                    resource_id=row.id,
                    title=row.display_name or row.title or "مشاور",
                    subtitle=row.title or specialty_text or row.bio,
                    route=f"/consultants/{row.id}",
                    province_id=row.province_id,
                    city_id=row.city_id,
                    rating=row.rating_average,
                    relevance_score=search_relevance_score(
                        query.q,
                        row.display_name,
                        row.title,
                        row.bio,
                        row.province_name,
                        row.city_name,
                        *(link.specialty.title for link in row.specialty_links),
                        *(link.specialty.code for link in row.specialty_links),
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
