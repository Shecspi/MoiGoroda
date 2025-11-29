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
from django.db.models.functions.datetime import TruncDate, TruncDay

from city.models import VisitedCity
from country.models import VisitedCountry
from dashboard.schemas import DailyStatistics, DaysPath, Quantity
from django_modern_rest import Controller, Path
from django_modern_rest.plugins.msgspec import MsgspecSerializer
from utils.decorators import is_superuser_json


@is_superuser_json
class GetNumberOfUsersController(Controller[MsgspecSerializer]):
    """
    Количество пользователей в системе
    """

    def get(self) -> Quantity:
        number_of_users = User.objects.count()
        return Quantity(count=number_of_users)


@is_superuser_json
class GetNumberOfRegistrationsYesterdayController(Controller[MsgspecSerializer]):
    """
    Количество регистраций за вчера
    """

    def get(self) -> Quantity:
        qty = User.objects.filter(date_joined__date=date.today() - timedelta(days=1)).count()
        return Quantity(count=qty)


@is_superuser_json
class GetNumberOfRegistrationsWeekController(Controller[MsgspecSerializer]):
    """
    Количество регистраций за неделю
    """

    def get(self) -> Quantity:
        qty = (
            User.objects.annotate(day=TruncDay('date_joined', tzinfo=timezone.utc))
            .filter(day__range=[date.today() - timedelta(days=7), date.today() - timedelta(days=1)])
            .count()
        )
        return Quantity(count=qty)


@is_superuser_json
class GetNumberOfRegistrationsMonthController(Controller[MsgspecSerializer]):
    """
    Количество регистраций за месяц
    """

    def get(self) -> Quantity:
        qty = (
            User.objects.annotate(day=TruncDay('date_joined', tzinfo=timezone.utc))
            .filter(
                day__range=[date.today() - timedelta(days=30), date.today() - timedelta(days=1)]
            )
            .count()
        )
        return Quantity(count=qty)


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

        return [DailyStatistics(date=item['date'], count=item['count']) for item in queryset]
