import json
from json import JSONDecodeError
from typing import NoReturn

from pydantic import ValidationError
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ParseError

from account.models import ShareSettings
from city.serializers import VisitedCitySerializer, NotVisitedCitySerializer
from city.structs import UserID
from services import logger
from services.db.visited_city_repo import get_visited_cities_many_users, get_not_visited_cities
from subscribe.repository import is_subscribed


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

    def __init__(self) -> None:
        # Список ID пользователей, у которых необходимо вернуть посещённые города
        self.user_id: list = []

        super().__init__()

    def _validate_json(self, data: str) -> None | NoReturn:
        try:
            UserID.model_validate_json(data)
        except ValidationError:
            logger.warning(
                self.request,
                '(API) An incorrect list of user IDs was received',
            )
            raise ParseError('Получен некорректный список идентификаторов пользователей')

    def _load_json(self, data: str) -> dict | NoReturn:
        try:
            return json.loads(data)
        except JSONDecodeError:
            logger.warning(
                self.request,
                '(API) An incorrect list of user IDs was received',
            )
            raise ParseError('Получен некорректный список идентификаторов пользователей')

    def _user_has_allowed_to_subscribe_to_himself(self, user_id: int) -> bool:
        try:
            user_settings = ShareSettings.objects.get(user_id=user_id)
        except ShareSettings.DoesNotExist:
            logger.warning(
                self.request,
                f'(API) Attempt to get a list of the cities of a user who did not change initial settings '
                f'(from #{self.request.user.id}, to #{user_id})',
            )
        else:
            if user_settings.can_subscribe:
                return True
            else:
                logger.warning(
                    self.request,
                    f'(API) Attempt to get a list of the cities of a user who did not allow it '
                    f'(from #{self.request.user.id}, to #{user_id})',
                )
        return False

    def _is_subscription_exists(self, to_id: int) -> bool:
        from_id = self.request.user.pk
        if is_subscribed(from_id, to_id):
            return True
        else:
            logger.warning(
                self.request,
                f'(API) Attempt to get a list of the cities of a user for whom do not have a subscription '
                f'(from #{from_id}, to #{to_id})',
            )
            return False

    def get(self, *args, **kwargs):
        input_data = self.request.GET.get('data')

        self._validate_json(input_data)

        # По идее ошибок загрузки JSON быть не должно, так как его уже проверил Pydantic,
        # но на всякий случай обрабатываю эту ситуацию.
        json_data = self._load_json(input_data)

        user_id = json_data.get('id')

        if not self.request.user.is_superuser:
            # Убираем из списка ID тех пользователей, которые не разрешили подписываться на себя.
            # Вообще это нештатная ситуация, но теоритически возможная, когда пользователь запретил
            # подписываться после того, как была открыта страница с картой, но до того, как запрос пришёл на сервер.
            for id in user_id:
                if self._user_has_allowed_to_subscribe_to_himself(
                    id
                ) and self._is_subscription_exists(id):
                    self.user_id.append(id)
                    logger.info(
                        self.request,
                        f'(API) Successful request for a list of visited cities from subscriptions '
                        f'(from #{self.request.user.id}, to #{id})',
                    )
        else:
            self.user_id = user_id

            logger.info(
                self.request,
                f'(API) Successful request from superuser for a list of visited cities from subscriptions (user #{self.request.user.id})',
            )

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

    def get(self, *args, **kwargs):
        logger.info(
            self.request,
            f'(API) Successful request for a list of not visited cities (user #{self.request.user.id})',
        )

        return super().get(*args, **kwargs)

    def get_queryset(self):
        return get_not_visited_cities(self.request.user.pk)
