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
