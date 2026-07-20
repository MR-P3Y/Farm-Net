from app.common.search import (
    SearchProvider,
    SearchResultType,
    SearchSort,
    UnifiedSearchGroup,
    UnifiedSearchQuery,
    UnifiedSearchResult,
    search_relevance_score,
)
from app.modules.social.enums import SocialDiscoverySort
from app.modules.social.repository import SocialRepository


class SocialSearchProvider(SearchProvider):
    result_type = SearchResultType.SOCIAL_POST

    def __init__(self, db, repository: SocialRepository | None = None) -> None:
        self.repo = repository or SocialRepository(db)

    def search(self, query: UnifiedSearchQuery) -> UnifiedSearchGroup:
        sort = (
            SocialDiscoverySort.NEWEST
            if query.sort == SearchSort.NEWEST
            else SocialDiscoverySort.RELEVANCE
        )
        filters = query.filters
        rows, total = self.repo.list_published_posts(
            category_id=filters.social_category_id,
            post_type=filters.social_post_type,
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
                title=row.title,
                subtitle=row.body[:500],
                route=f"/social/detail/{row.id}",
                province_id=row.province_id,
                city_id=row.city_id,
                relevance_score=search_relevance_score(
                    query.q,
                    row.title,
                    row.body,
                    row.province_name,
                    row.city_name,
                    row.village_name,
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
