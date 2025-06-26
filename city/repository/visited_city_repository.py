from typing import Sequence

from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import Avg, F, Count

from city.models import VisitedCity
from city.repository.interfaces import AbstractVisitedCityRepository


class VisitedCityRepository(AbstractVisitedCityRepository):
    def get_average_rating(self, city_id: int) -> float:
        """
        Возвращает средний рейтинг города city на основе оценок всех пользователей,
        округлённый с точностью до 0,5.
        """
        not_rounded_average_rating = float(
            VisitedCity.objects.filter(city_id=city_id).aggregate(Avg('rating'))['rating__avg'] or 0
        )
        return round(not_rounded_average_rating * 2) / 2

    def count_user_visits(self, city_id: int, user: AbstractBaseUser) -> int:
        """
        Возвращает количество посещений города city указанным пользователем user.
        """
        return VisitedCity.objects.filter(city_id=city_id, user=user).count()

    def count_all_visits(self, city_id: int) -> int:
        """
        Возвращает количество посещений города city всеми пользователями.
        """
        return VisitedCity.objects.filter(city_id=city_id).count()

    def get_popular_months(self, city_id: int) -> list[int]:
        """
        Возвращает номера 3 месяцев, в которых находится больше всего посещений города city.
        """
        return list(
            VisitedCity.objects.filter(city_id=city_id, date_of_visit__isnull=False)
            .annotate(month=F('date_of_visit__month'))
            .values('month')
            .annotate(visits=Count('id'))
            .order_by('-visits')
            .values_list('month', flat=True)[:3]
        )

    def get_user_visits(self, city_id: int, user: AbstractBaseUser) -> Sequence[dict]:
        """
        Возвращает список всех посещений города city пользователем user.
        Возвращаются поля id, date_of_visit, rating, impression, city__title.
        """
        return list(
            VisitedCity.objects.filter(user=user, city_id=city_id)
            .select_related('city')
            .order_by(F('date_of_visit').desc(nulls_last=True))
            .values('id', 'date_of_visit', 'rating', 'impression', 'city__title')
        )

    def get_number_of_users_who_visit_city(self, city_id: int) -> int:
        """
        Возвращает количество пользователей, посетивших город с city_id.
        """
        return VisitedCity.objects.filter(city_id=city_id, is_first_visit=True).count()
