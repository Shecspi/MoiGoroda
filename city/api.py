import json

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from account.models import ShareSettings
from city.serializers import VisitedCitySerializer, NotVisitedCitySerializer
from services import logger
from services.db.visited_city_repo import get_visited_cities_many_users, get_not_visited_cities


class GetVisitedCities(generics.ListAPIView):
    serializer_class = VisitedCitySerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']

    def get(self, *args, **kwargs):
        logger.info(
            self.request,
            f'(API) Successful request for a list of visited cities (user #{self.request.user.id})',
        )

        return super().get(*args, **kwargs)

    def get_queryset(self):
        user_id = self.request.user.pk

        return get_visited_cities_many_users(
            [user_id],
            ('city', 'user'),
            [
                'user__username',
                'id',
                'city__title',
                'city__coordinate_width',
                'city__coordinate_longitude',
                'date_of_visit',
            ],
        )


class GetVisitedCitiesFromSubscriptions(generics.ListAPIView):
    serializer_class = VisitedCitySerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']

    def __init__(self):
        # Список ID пользователей, у которых необходимо вернуть посещённые города
        self.user_id: list = []

        super().__init__()

    def get(self, *args, **kwargs):
        input_data = self.request.GET.get('data')
        json_data = json.loads(input_data)
        user_id = json_data.get('ids')

        if not self.request.user.is_superuser:
            # Убираем из списка ID тех пользователей, которые не разрешили подписываться на себя.
            # Вообще это нештатная ситуация, но теоритически возможная, когда пользователь запретил
            # подписываться после того, как была открыта страница с картой, но до того, как запрос пришёл на сервер.
            for id in user_id:
                try:
                    user_settings = ShareSettings.objects.get(id=id)
                except ShareSettings.DoesNotExist:
                    logger.warning(
                        self.request,
                        '(Share settings) Attempt to get a list of the cities of a user who did not change initial '
                        'settings',
                    )
                else:
                    if user_settings.can_subscribe:
                        self.user_id.append(id)
                    else:
                        logger.warning(
                            self.request,
                            '(Share settings) Attempt to get a list of the cities of a user who did not allow it',
                        )
        else:
            self.user_id = user_id

        return super().get(*args, **kwargs)

    def get_queryset(self):
        return get_visited_cities_many_users(
            self.user_id,
            ('city', 'user'),
            [
                'user__username',
                'city__id',
                'city__title',
                'city__coordinate_width',
                'city__coordinate_longitude',
            ],
        )


class GetNotVisitedCities(generics.ListAPIView):
    serializer_class = NotVisitedCitySerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']

    def get_queryset(self):
        return get_not_visited_cities(self.request.user.pk)
