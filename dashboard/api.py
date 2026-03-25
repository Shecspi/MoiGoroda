"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import date, datetime, timedelta, timezone

from django.contrib.auth.models import User
from django.db.models import Count, F, Func, Max, OuterRef, Subquery, Sum, Value
from django.db.models.fields import CharField
from django.db.models.functions.datetime import TruncDate, TruncDay, TruncMonth, TruncWeek

from city.models import VisitedCity
from collection.models import PersonalCollection
from country.models import VisitedCountry
from dashboard.schemas import (
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


def _get_group_trunc_function(
    group_by: str,
) -> type[TruncDay] | type[TruncWeek] | type[TruncMonth]:
    if group_by == 'day':
        return TruncDay
    if group_by == 'week':
        return TruncWeek
    if group_by == 'month':
        return TruncMonth
    raise ValueError('group_by must be one of: day, week, month')


def _format_group_label(group_date: date, group_by: str) -> str:
    if group_by == 'day':
        return group_date.strftime('%d.%m.%Y')
    if group_by == 'week':
        iso_year, iso_week, _ = group_date.isocalendar()
        return f'{iso_week:02d}.{iso_year}'
    return group_date.strftime('%m.%Y')


def _next_group_date(group_date: date, group_by: str) -> date:
    if group_by == 'day':
        return group_date + timedelta(days=1)
    if group_by == 'week':
        return group_date + timedelta(weeks=1)

    # Переход на первый день следующего месяца
    if group_date.month == 12:
        return date(group_date.year + 1, 1, 1)
    return date(group_date.year, group_date.month + 1, 1)


def _collect_registrations_by_group(
    date_from: date,
    date_to: date,
    group_by: str,
) -> list[DailyStatistics]:
    trunc_fn = _get_group_trunc_function(group_by)
    queryset = (
        User.objects.filter(
            date_joined__date__range=[date_from, date_to],
        )
        .annotate(group_date=TruncDate(trunc_fn('date_joined', tzinfo=timezone.utc)))
        .values('group_date')
        .annotate(count=Count('id'))
        .order_by('group_date')
    )

    grouped_data = {item['group_date']: item['count'] for item in queryset}

    if not grouped_data:
        return []

    first_date = min(grouped_data.keys())
    last_date = max(grouped_data.keys())

    result: list[DailyStatistics] = []
    current_date = first_date
    while current_date <= last_date:
        result.append(
            DailyStatistics(
                label=_format_group_label(current_date, group_by),
                count=grouped_data.get(current_date, 0),
            )
        )
        current_date = _next_group_date(current_date, group_by)

    return result


def _collect_added_visited_cities_by_group(
    date_from: date,
    date_to: date,
    group_by: str,
) -> list[DailyStatistics]:
    trunc_fn = _get_group_trunc_function(group_by)
    queryset = (
        VisitedCity.objects.filter(
            created_at__date__range=[date_from, date_to],
        )
        .annotate(group_date=TruncDate(trunc_fn('created_at', tzinfo=timezone.utc)))
        .values('group_date')
        .annotate(count=Count('id'))
        .order_by('group_date')
    )

    grouped_data = {item['group_date']: item['count'] for item in queryset}

    if not grouped_data:
        return []

    first_date = min(grouped_data.keys())
    last_date = max(grouped_data.keys())

    result: list[DailyStatistics] = []
    current_date = first_date
    while current_date <= last_date:
        result.append(
            DailyStatistics(
                label=_format_group_label(current_date, group_by),
                count=grouped_data.get(current_date, 0),
            )
        )
        current_date = _next_group_date(current_date, group_by)

    return result


def _collect_added_visited_countries_by_group(
    date_from: date,
    date_to: date,
    group_by: str,
) -> list[DailyStatistics]:
    trunc_fn = _get_group_trunc_function(group_by)
    queryset = (
        VisitedCountry.objects.filter(
            added_at__date__range=[date_from, date_to],
        )
        .annotate(group_date=TruncDate(trunc_fn('added_at', tzinfo=timezone.utc)))
        .values('group_date')
        .annotate(count=Count('id'))
        .order_by('group_date')
    )

    grouped_data = {item['group_date']: item['count'] for item in queryset}

    if not grouped_data:
        return []

    first_date = min(grouped_data.keys())
    last_date = max(grouped_data.keys())

    result: list[DailyStatistics] = []
    current_date = first_date
    while current_date <= last_date:
        result.append(
            DailyStatistics(
                label=_format_group_label(current_date, group_by),
                count=grouped_data.get(current_date, 0),
            )
        )
        current_date = _next_group_date(current_date, group_by)

    return result


def _collect_places_by_group(
    date_from: date,
    date_to: date,
    group_by: str,
) -> list[DailyStatistics]:
    trunc_fn = _get_group_trunc_function(group_by)
    queryset = (
        Place.objects.filter(
            created_at__date__range=[date_from, date_to],
        )
        .annotate(group_date=TruncDate(trunc_fn('created_at', tzinfo=timezone.utc)))
        .values('group_date')
        .annotate(count=Count('id'))
        .order_by('group_date')
    )

    grouped_data = {item['group_date']: item['count'] for item in queryset}
    if not grouped_data:
        return []

    first_date = min(grouped_data.keys())
    last_date = max(grouped_data.keys())

    result: list[DailyStatistics] = []
    current_date = first_date
    while current_date <= last_date:
        result.append(
            DailyStatistics(
                label=_format_group_label(current_date, group_by),
                count=grouped_data.get(current_date, 0),
            )
        )
        current_date = _next_group_date(current_date, group_by)

    return result


def _collect_personal_collections_by_group(
    date_from: date,
    date_to: date,
    group_by: str,
) -> list[DailyStatistics]:
    trunc_fn = _get_group_trunc_function(group_by)
    queryset = (
        PersonalCollection.objects.filter(
            created_at__date__range=[date_from, date_to],
        )
        .annotate(group_date=TruncDate(trunc_fn('created_at', tzinfo=timezone.utc)))
        .values('group_date')
        .annotate(count=Count('id'))
        .order_by('group_date')
    )

    grouped_data = {item['group_date']: item['count'] for item in queryset}
    if not grouped_data:
        return []

    first_date = min(grouped_data.keys())
    last_date = max(grouped_data.keys())

    result: list[DailyStatistics] = []
    current_date = first_date
    while current_date <= last_date:
        result.append(
            DailyStatistics(
                label=_format_group_label(current_date, group_by),
                count=grouped_data.get(current_date, 0),
            )
        )
        current_date = _next_group_date(current_date, group_by)

    return result


@is_superuser_json
class GetNumberOfUsersController(Controller[MsgspecSerializer]):
    """
    Количество пользователей в системе
    """

    def get(self) -> Quantity:
        number_of_users = User.objects.count()
        return Quantity(count=number_of_users)


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
class GetTotalVisitedPlacesController(Controller[MsgspecSerializer]):
    def get(self) -> Quantity:
        qty = Place.objects.count()
        return Quantity(count=qty)


@is_superuser_json
class GetPersonalCollectionsTotalController(Controller[MsgspecSerializer]):
    def get(self) -> Quantity:
        qty = PersonalCollection.objects.count()
        return Quantity(count=qty)


@is_superuser_json
class GetPublicPersonalCollectionsTotalController(Controller[MsgspecSerializer]):
    def get(self) -> Quantity:
        qty = PersonalCollection.objects.filter(is_public=True).count()
        return Quantity(count=qty)


@is_superuser_json
class GetTotalVisitedOnlyPlacesController(Controller[MsgspecSerializer]):
    def get(self) -> Quantity:
        qty = Place.objects.filter(is_visited=True).count()
        return Quantity(count=qty)


@is_superuser_json
class GetPlacesByRangeController(Query[RegistrationsRangeQuery], Controller[MsgspecSerializer]):
    def get(self) -> list[DailyStatistics]:
        group_by = self.parsed_query.group_by
        if group_by not in {'day', 'week', 'month'}:
            raise ValueError('group_by must be one of: day, week, month')
        if self.parsed_query.date_from > self.parsed_query.date_to:
            raise ValueError('date_from must be less than or equal to date_to')

        return _collect_places_by_group(
            date_from=self.parsed_query.date_from,
            date_to=self.parsed_query.date_to,
            group_by=group_by,
        )


@is_superuser_json
class GetPlacesComparisonController(Query[RegistrationsComparisonQuery], Controller[MsgspecSerializer]):
    def get(self) -> PeriodComparisonStatistics:
        date_from = self.parsed_query.date_from
        date_to = self.parsed_query.date_to
        if date_from > date_to:
            raise ValueError('date_from must be less than or equal to date_to')

        current_count = Place.objects.filter(created_at__date__range=[date_from, date_to]).count()

        period_days = (date_to - date_from).days + 1
        previous_date_to = date_from - timedelta(days=1)
        previous_date_from = previous_date_to - timedelta(days=period_days - 1)
        previous_count = Place.objects.filter(
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
class GetPersonalCollectionsByRangeController(
    Query[RegistrationsRangeQuery], Controller[MsgspecSerializer]
):
    def get(self) -> list[DailyStatistics]:
        group_by = self.parsed_query.group_by
        if group_by not in {'day', 'week', 'month'}:
            raise ValueError('group_by must be one of: day, week, month')
        if self.parsed_query.date_from > self.parsed_query.date_to:
            raise ValueError('date_from must be less than or equal to date_to')

        return _collect_personal_collections_by_group(
            date_from=self.parsed_query.date_from,
            date_to=self.parsed_query.date_to,
            group_by=group_by,
        )


@is_superuser_json
class GetPersonalCollectionsComparisonController(
    Query[RegistrationsComparisonQuery], Controller[MsgspecSerializer]
):
    def get(self) -> PeriodComparisonStatistics:
        date_from = self.parsed_query.date_from
        date_to = self.parsed_query.date_to
        if date_from > date_to:
            raise ValueError('date_from must be less than or equal to date_to')

        current_count = PersonalCollection.objects.filter(
            created_at__date__range=[date_from, date_to]
        ).count()

        period_days = (date_to - date_from).days + 1
        previous_date_to = date_from - timedelta(days=1)
        previous_date_from = previous_date_to - timedelta(days=period_days - 1)
        previous_count = PersonalCollection.objects.filter(
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
class GetTotalVisitedCitiesVisitsController(Controller[MsgspecSerializer]):
    """
    Количество посещений городов всеми пользователями
    """

    def get(self) -> Quantity:
        qty = VisitedCity.objects.count()
        return Quantity(count=qty)


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
class GetTotalVisitedCountriesController(Controller[MsgspecSerializer]):
    def get(self) -> Quantity:
        qty = VisitedCountry.objects.count()
        return Quantity(count=qty)


@is_superuser_json
class GetUsersWithVisitedCountriesController(Controller[MsgspecSerializer]):
    def get(self) -> Quantity:
        qty = VisitedCountry.objects.values('user').distinct().count()
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
class GetAddedVisitedCountryController(Path[DaysPath], Controller[MsgspecSerializer]):
    def get(self) -> Quantity:
        start_date = datetime.now().date() - timedelta(days=self.parsed_path.days)
        finish_date = datetime.now().date() + timedelta(days=1)
        qty = VisitedCountry.objects.filter(added_at__range=[start_date, finish_date]).count()
        return Quantity(count=qty)


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
