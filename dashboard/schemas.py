import msgspec
from datetime import date


class Quantity(msgspec.Struct):
    count: int


class DailyStatistics(msgspec.Struct):
    label: str
    count: int


class UserStatistics(msgspec.Struct):
    label: str
    count: int


class DaysPath(msgspec.Struct):
    days: int


class RegistrationsRangeQuery(msgspec.Struct):
    date_from: date
    date_to: date
    group_by: str = 'day'


class RegistrationsComparisonQuery(msgspec.Struct):
    date_from: date
    date_to: date


class PeriodComparisonStatistics(msgspec.Struct):
    current_count: int
    previous_count: int
    delta: int
    delta_percent: float


class TrendCardOverview(msgspec.Struct):
    comparison: PeriodComparisonStatistics
    chart: list[DailyStatistics]


class PlacesOverviewResponse(msgspec.Struct):
    total_visited_places: Quantity
    total_visited_only_places: Quantity
    last_30d: TrendCardOverview
    last_6m: TrendCardOverview
    last_1y: TrendCardOverview


class PersonalCollectionsOverviewResponse(msgspec.Struct):
    total_personal_collections: Quantity
    total_public_personal_collections: Quantity
    last_30d: TrendCardOverview
    last_6m: TrendCardOverview
    last_1y: TrendCardOverview


class VisitedCountriesOverviewResponse(msgspec.Struct):
    total_visited_countries: Quantity
    users_with_visited_countries: Quantity
    added_last_30d: TrendCardOverview
    added_last_6m: TrendCardOverview
    added_last_1y: TrendCardOverview


class VisitedCitiesOverviewResponse(msgspec.Struct):
    total_visited_cities_visits: Quantity
    unique_visited_cities: Quantity
    added_last_30d: TrendCardOverview
    added_last_6m: TrendCardOverview
    added_last_1y: TrendCardOverview
    visited_by_user_chart: list[UserStatistics]
    unique_visited_by_user_chart: list[UserStatistics]


class UsersOverviewResponse(msgspec.Struct):
    total_users: Quantity
    users_without_visited_cities: Quantity
    registrations_last_30d: TrendCardOverview
    registrations_last_6m: TrendCardOverview
    registrations_last_1y: TrendCardOverview


class BlogArticlesPageQuery(msgspec.Struct):
    page: int = 1
    per_page: int = 10


class BlogArticleTableRow(msgspec.Struct):
    id: int
    title: str
    slug: str
    published_date: str
    view_count_total: int
    detail_url: str


class BlogArticlesPageResponse(msgspec.Struct):
    page: int
    total_pages: int
    per_page: int
    total_count: int
    items: list[BlogArticleTableRow]


class BlogArticlesCardOverview(msgspec.Struct):
    items: list[BlogArticleTableRow]
    comparison: PeriodComparisonStatistics
    chart: list[DailyStatistics]


class BlogArticlesOverviewResponse(msgspec.Struct):
    added_last_30d: BlogArticlesCardOverview
    top_views_60d: BlogArticlesCardOverview
