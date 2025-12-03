from django.contrib.auth.models import User
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import (
    OuterRef,
    Q,
    Min,
    Max,
    Avg,
    Exists,
    Count,
    Subquery,
    IntegerField,
    Value,
    QuerySet,
)
from django.db.models.functions import Round

from city.models import VisitedCity, City
from collection.models import Collection


def get_all_cities_from_collection(
    collection_id: int, user: User | None = None
) -> QuerySet[City, City]:
    """
    Возвращает все города в коллекции с ID = collection_id.
    Если указан user, то возвращаемый QuerySet аннотируется дополнительными полями.
    """
    cities_id = [city.id for city in Collection.objects.get(id=collection_id).city.all()]

    if user:
        base_qs = VisitedCity.objects.filter(user=user, city=OuterRef('pk'))

        # Подзапрос для сбора всех дат посещений города
        visit_dates_subquery = (
            base_qs.values('city')
            .annotate(
                visit_dates=ArrayAgg('date_of_visit', distinct=False, filter=~Q(date_of_visit=None))
            )
            .values('visit_dates')
        )

        # Подзапрос для даты первого посещения (first_visit_date)
        first_visit_date_subquery = (
            base_qs.values('city')
            .annotate(first_visit_date=Min('date_of_visit'))
            .values('first_visit_date')
        )

        # Подзапрос для даты последнего посещения (first_visit_date)
        last_visit_date_subquery = (
            base_qs.values('city')
            .annotate(last_visit_date=Max('date_of_visit'))
            .values('last_visit_date')
        )

        # Подзапрос для вычисления среднего рейтинга посещений города пользователем
        average_rating_subquery = (
            base_qs.values('city_id')  # Группировка по городу
            .annotate(avg_rating=Avg('rating'))  # Вычисление среднего рейтинга
            .values('avg_rating')  # Передаем только рейтинг
        )

        # Есть ли сувенир из города?
        has_souvenir = Exists(base_qs.filter(has_magnet=True))

        # Подзапрос для количества посещений города пользователем
        city_visits_subquery = (
            base_qs.values('city_id')  # Группировка по городу
            .annotate(count=Count('*'))  # Подсчет записей (число посещений)
            .values('count')  # Передаем только поле count
        )

        # Подзапрос для получения количество пользователей, посетивших город
        number_of_users_who_visit_city = (
            VisitedCity.objects.filter(city=OuterRef('pk'), is_first_visit=True)
            .values('city')
            .annotate(count=Count('*'))
            .values('count')[:1]
        )

        # Подзапрос для получения общего количества посещений города
        number_of_visits_all_users = (
            VisitedCity.objects.filter(city=OuterRef('pk'))
            .values('city')
            .annotate(count=Count('*'))
            .values('count')[:1]
        )

        return (
            City.objects.filter(id__in=cities_id)
            .select_related('region', 'country')
            .annotate(
                is_visited=Exists(VisitedCity.objects.filter(city_id=OuterRef('pk'), user=user)),
                visit_dates=Subquery(visit_dates_subquery),
                first_visit_date=Subquery(first_visit_date_subquery),
                last_visit_date=Subquery(last_visit_date_subquery),
                average_rating=(
                    Round((Subquery(average_rating_subquery) * 2), 0) / 2
                ),  # Округление до 0.5
                has_souvenir=has_souvenir,
                number_of_visits=Subquery(city_visits_subquery, output_field=IntegerField()),
                number_of_users_who_visit_city=Subquery(
                    number_of_users_who_visit_city, output_field=IntegerField()
                ),
                number_of_visits_all_users=Subquery(number_of_visits_all_users),
            )
        )
    else:
        # Подзапрос для получения количество пользователей, посетивших город
        number_of_users_who_visit_city = (
            VisitedCity.objects.filter(city=OuterRef('pk'), is_first_visit=True)
            .values('city')
            .annotate(count=Count('*'))
            .values('count')[:1]
        )

        # Подзапрос для получения общего количества посещений города
        number_of_visits_all_users = (
            VisitedCity.objects.filter(city=OuterRef('pk'))
            .values('city')
            .annotate(count=Count('*'))
            .values('count')[:1]
        )

        return (
            City.objects.filter(id__in=cities_id)
            .select_related('region', 'country')
            .annotate(
                is_visited=Value(False),
                number_of_users_who_visit_city=Subquery(
                    number_of_users_who_visit_city, output_field=IntegerField()
                ),
                number_of_visits_all_users=Subquery(number_of_visits_all_users),
            )
        )
