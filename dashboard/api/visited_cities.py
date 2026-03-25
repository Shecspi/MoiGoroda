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
class GetAddedVisitedCitiesByRangeController(
    Query[RegistrationsRangeQuery], Controller[MsgspecSerializer]
):
    """
    Количество добавленных посещённых городов по диапазону и группировке
    """

    def get(self) -> list[DailyStatistics]:
        group_by = self.parsed_query.group_by
        if group_by not in {'day', 'week', 'month'}:
            raise ValueError('group_by must be one of: day, week, month')

        if self.parsed_query.date_from > self.parsed_query.date_to:
            raise ValueError('date_from must be less than or equal to date_to')

        return _collect_added_visited_cities_by_group(
            date_from=self.parsed_query.date_from,
            date_to=self.parsed_query.date_to,
            group_by=group_by,
        )

@is_superuser_json
class GetAddedVisitedCitiesComparisonController(
    Query[RegistrationsComparisonQuery], Controller[MsgspecSerializer]
):
    """
    Сравнение количества добавленных посещённых городов с предыдущим периодом
    """

    def get(self) -> PeriodComparisonStatistics:
        date_from = self.parsed_query.date_from
        date_to = self.parsed_query.date_to

        if date_from > date_to:
            raise ValueError('date_from must be less than or equal to date_to')

        current_count = VisitedCity.objects.filter(created_at__date__range=[date_from, date_to]).count()

        period_days = (date_to - date_from).days + 1
        previous_date_to = date_from - timedelta(days=1)
        previous_date_from = previous_date_to - timedelta(days=period_days - 1)
        previous_count = VisitedCity.objects.filter(
            created_at__date__range=[previous_date_from, previous_date_to]
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
class GetAverageQtyUniqueVisitedCitiesController(Controller[MsgspecSerializer]):
    """
    Среднее количество уникальных городов на пользователя
    """

    def get(self) -> Quantity:
        total_visited_cities = (
            VisitedCity.objects.values('user')
            .annotate(unique_cities=Count('city', distinct=True))
            .aggregate(total=Sum('unique_cities'))
            .get('total', 0)
            or 0
        )
        total_users = VisitedCity.objects.values('user').distinct().count()
        queryset = 0 if total_users == 0 else int(total_visited_cities / total_users)
        return Quantity(count=queryset)

@is_superuser_json
class GetAverageQtyVisitedCitiesController(Controller[MsgspecSerializer]):
    """
    Среднее количество посещений городов на пользователя
    """

    def get(self) -> Quantity:
        total_visited_cities = VisitedCity.objects.count()
        total_users = VisitedCity.objects.values('user').distinct().count()
        queryset = 0 if total_users == 0 else int(total_visited_cities / total_users)
        return Quantity(count=queryset)

@is_superuser_json
class GetMaxQtyUniqueVisitedCitiesController(Controller[MsgspecSerializer]):
    """
    Максимальное количество уникальных городов на пользователя
    """

    def get(self) -> Quantity:
        queryset = (
            VisitedCity.objects.values('user')
            .annotate(unique_cities=Count('city', distinct=True))
            .order_by('-unique_cities')[:1]
        )

        return Quantity(count=queryset[0]['unique_cities'])

@is_superuser_json
class GetMaxQtyVisitedCitiesController(Controller[MsgspecSerializer]):
    """
    Максимальное количество посещений городов на пользователя
    """

    def get(self) -> Quantity:
        queryset = (
            VisitedCity.objects.values('user')
            .annotate(unique_cities=Count('city'))
            .order_by('-unique_cities')[:1]
        )

        return Quantity(count=queryset[0]['unique_cities'])

@is_superuser_json
class GetTotalVisitedCitiesVisitsController(Controller[MsgspecSerializer]):
    """
    Количество посещений городов всеми пользователями
    """

    def get(self) -> Quantity:
        qty = VisitedCity.objects.count()
        return Quantity(count=qty)

@is_superuser_json
class GetUniqueVisitedCitiesByUserChartController(Controller[MsgspecSerializer]):
    """
    Данные для графика количества уникальных городов по каждому пользователю
    """

    def get(self) -> list[UserStatistics]:
        queryset = (
            User.objects.annotate(
                qty_unique_visited_cities=Subquery(
                    VisitedCity.objects.filter(user=OuterRef('pk'))
                    .values('user')
                    .annotate(qty=Count('city', distinct=True))
                    .values('qty')
                )
            )
            .values('username', 'qty_unique_visited_cities')
            .exclude(qty_unique_visited_cities=None)
            .order_by('-qty_unique_visited_cities')[:50]
        )

        result = [
            UserStatistics(label=item['username'], count=item['qty_unique_visited_cities'])
            for item in queryset
        ]
        return list(reversed(result))

@is_superuser_json
class GetUniqueVisitedCitiesController(Controller[MsgspecSerializer]):
    """
    Количество уникальных городов, посещенных всеми пользователями
    """

    def get(self) -> Quantity:
        qty = (
            VisitedCity.objects.values('user')
            .annotate(unique_cities=Count('city', distinct=True))
            .aggregate(total=Sum('unique_cities'))
            .get('total', 0)
            or 0
        )
        return Quantity(count=qty)

@is_superuser_json
class GetVisitedCitiesByUserChartController(Controller[MsgspecSerializer]):
    """
    Данные для графика общего количества посещений городов по каждому пользователю
    """

    def get(self) -> list[UserStatistics]:
        queryset = (
            User.objects.annotate(
                qty_visited_cities=Subquery(
                    VisitedCity.objects.filter(user=OuterRef('pk'))
                    .values('user')
                    .annotate(qty=Count('pk'))
                    .values('qty')
                )
            )
            .values('username', 'qty_visited_cities')
            .exclude(qty_visited_cities=None)
            .order_by('-qty_visited_cities')[:50]
        )

        result = [
            UserStatistics(label=item['username'], count=item['qty_visited_cities'])
            for item in queryset
        ]
        return list(reversed(result))

