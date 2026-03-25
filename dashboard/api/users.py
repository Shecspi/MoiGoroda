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
class GetNumberOfUsersController(Controller[MsgspecSerializer]):
    """
    Количество пользователей в системе
    """

    def get(self) -> Quantity:
        number_of_users = User.objects.count()
        return Quantity(count=number_of_users)

@is_superuser_json
class GetNumberOfUsersWithoutVisitedCitiesController(Controller[MsgspecSerializer]):
    """
    Количество пользователей, у которых нет посещений городов
    (то есть они зарегистрировались в системе, но не посетили ни одного города)
    """

    def get(self) -> Quantity:
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
            .filter(qty_visited_cities=None)
            .order_by('-qty_visited_cities')
        )
        return Quantity(count=queryset.count())

@is_superuser_json
class GetRegistrationsByRangeController(
    Query[RegistrationsRangeQuery], Controller[MsgspecSerializer]
):
    """
    Количество регистраций по заданному диапазону и группировке
    """

    def get(self) -> list[DailyStatistics]:
        group_by = self.parsed_query.group_by
        if group_by not in {'day', 'week', 'month'}:
            raise ValueError('group_by must be one of: day, week, month')

        if self.parsed_query.date_from > self.parsed_query.date_to:
            raise ValueError('date_from must be less than or equal to date_to')

        return _collect_registrations_by_group(
            date_from=self.parsed_query.date_from,
            date_to=self.parsed_query.date_to,
            group_by=group_by,
        )

@is_superuser_json
class GetRegistrationsComparisonController(
    Query[RegistrationsComparisonQuery], Controller[MsgspecSerializer]
):
    """
    Сравнение регистраций с предыдущим равным периодом
    """

    def get(self) -> PeriodComparisonStatistics:
        date_from = self.parsed_query.date_from
        date_to = self.parsed_query.date_to

        if date_from > date_to:
            raise ValueError('date_from must be less than or equal to date_to')

        current_count = User.objects.filter(date_joined__date__range=[date_from, date_to]).count()

        period_days = (date_to - date_from).days + 1
        previous_date_to = date_from - timedelta(days=1)
        previous_date_from = previous_date_to - timedelta(days=period_days - 1)
        previous_count = User.objects.filter(
            date_joined__date__range=[previous_date_from, previous_date_to]
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
class GetRegistrationsCumulativeChartController(
    Query[RegistrationsRangeQuery], Controller[MsgspecSerializer]
):
    """
    Накопительный график регистраций по диапазону
    """

    def get(self) -> list[DailyStatistics]:
        group_by = self.parsed_query.group_by
        if group_by not in {'day', 'week', 'month'}:
            raise ValueError('group_by must be one of: day, week, month')

        if self.parsed_query.date_from > self.parsed_query.date_to:
            raise ValueError('date_from must be less than or equal to date_to')

        grouped = _collect_registrations_by_group(
            date_from=self.parsed_query.date_from,
            date_to=self.parsed_query.date_to,
            group_by=group_by,
        )

        cumulative = 0
        result: list[DailyStatistics] = []
        for item in grouped:
            cumulative += item.count
            result.append(DailyStatistics(label=item.label, count=cumulative))
        return result

