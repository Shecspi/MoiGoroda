"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import datetime, timedelta, timezone

from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, F, Func, Max, OuterRef, Q, Subquery, Sum, Value
from django.db.models.fields import CharField
from django.db.models.functions.datetime import TruncDate, TruncDay
from django.urls import reverse

from blog.models import BlogArticle, BlogArticleView
from city.models import VisitedCity
from collection.models import PersonalCollection
from country.models import VisitedCountry
from dashboard.schemas import (
    BlogArticleTableRow,
    BlogArticlesPageQuery,
    BlogArticlesPageResponse,
    DailyStatistics,
    DaysPath,
    PeriodComparisonStatistics,
    Quantity,
    RegistrationsComparisonQuery,
    RegistrationsRangeQuery,
    UserStatistics,
)
from dmr import Controller, Path, Query
from dmr.plugins.msgspec import MsgspecSerializer
from utils.decorators import is_superuser_json
from place.models import Place


from dashboard.statistics_helpers import (
    _collect_added_visited_cities_by_group,
    _collect_added_visited_countries_by_group,
    _collect_blog_article_views_by_group,
    _collect_blog_articles_added_by_group,
    _collect_personal_collections_by_group,
    _collect_places_by_group,
    _collect_registrations_by_group,
)


@is_superuser_json
class GetAddedVisitedCountriesByRangeController(
    Query[RegistrationsRangeQuery], Controller[MsgspecSerializer]
):
    """
    Количество добавленных посещённых стран по диапазону и группировке
    """

    def get(self) -> list[DailyStatistics]:
        group_by = self.parsed_query.group_by
        if group_by not in {'day', 'week', 'month'}:
            raise ValueError('group_by must be one of: day, week, month')

        if self.parsed_query.date_from > self.parsed_query.date_to:
            raise ValueError('date_from must be less than or equal to date_to')

        return _collect_added_visited_countries_by_group(
            date_from=self.parsed_query.date_from,
            date_to=self.parsed_query.date_to,
            group_by=group_by,
        )

@is_superuser_json
class GetAddedVisitedCountriesChartController(Controller[MsgspecSerializer]):
    """
    Данные для графика добавленных посещённых стран по дням
    """

    def get(self) -> list[DailyStatistics]:
        queryset = (
            VisitedCountry.objects.annotate(day=TruncDay('added_at', tzinfo=timezone.utc))
            .order_by('day')
            .annotate(
                date=Func(
                    TruncDate(F('day')),
                    Value('DD.MM.YYYY'),
                    function='to_char',
                    output_field=CharField(),
                )
            )
            .values('date')
            .annotate(count=Count('id'))[:50]
        )

        return [DailyStatistics(label=item['date'], count=item['count']) for item in queryset]

@is_superuser_json
class GetAddedVisitedCountriesComparisonController(
    Query[RegistrationsComparisonQuery], Controller[MsgspecSerializer]
):
    """
    Сравнение количества добавленных посещённых стран с предыдущим периодом
    """

    def get(self) -> PeriodComparisonStatistics:
        date_from = self.parsed_query.date_from
        date_to = self.parsed_query.date_to

        if date_from > date_to:
            raise ValueError('date_from must be less than or equal to date_to')

        current_count = VisitedCountry.objects.filter(added_at__date__range=[date_from, date_to]).count()

        period_days = (date_to - date_from).days + 1
        previous_date_to = date_from - timedelta(days=1)
        previous_date_from = previous_date_to - timedelta(days=period_days - 1)
        previous_count = VisitedCountry.objects.filter(
            added_at__date__range=[previous_date_from, previous_date_to]
        ).count()

        delta = current_count - previous_count
        delta_percent = 0.0 if previous_count == 0 else round((delta / previous_count) * 100, 2)
        return PeriodComparisonStatistics(
            current_count=current_count,
            previous_count=previous_count,
            delta=delta,
            delta_percent=delta_percent,
        )

@is_superuser_json
class GetAddedVisitedCountryController(Path[DaysPath], Controller[MsgspecSerializer]):
    def get(self) -> Quantity:
        start_date = datetime.now().date() - timedelta(days=self.parsed_path.days)
        finish_date = datetime.now().date() + timedelta(days=1)
        qty = VisitedCountry.objects.filter(added_at__range=[start_date, finish_date]).count()
        return Quantity(count=qty)

@is_superuser_json
class GetAverageQtyVisitedCountriesController(Controller[MsgspecSerializer]):
    def get(self) -> Quantity:
        total_visited_countries = VisitedCountry.objects.count()
        total_users = VisitedCountry.objects.values('user').distinct().count()
        qty = 0 if total_users == 0 else int(total_visited_countries / total_users)
        return Quantity(count=qty)

@is_superuser_json
class GetMaxQtyVisitedCountriesController(Controller[MsgspecSerializer]):
    def get(self) -> Quantity:
        max_qty = (
            VisitedCountry.objects.values('user')
            .annotate(countries_qty=Count('country'))
            .aggregate(value=Max('countries_qty'))
            .get('value')
            or 0
        )
        return Quantity(count=max_qty)

@is_superuser_json
class GetTotalVisitedCountriesController(Controller[MsgspecSerializer]):
    def get(self) -> Quantity:
        qty = VisitedCountry.objects.count()
        return Quantity(count=qty)

@is_superuser_json
class GetUsersWithVisitedCountriesController(Controller[MsgspecSerializer]):
    def get(self) -> Quantity:
        qty = VisitedCountry.objects.values('user').distinct().count()
        return Quantity(count=qty)

