"""
Реализует API для получения информации о посещённых и непосещённых городах.

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import json
from json import JSONDecodeError
from typing import NoReturn

from pydantic import ValidationError
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
import rest_framework.exceptions as drf_exc
from rest_framework.response import Response

from account.models import ShareSettings
from city.models import City
from city.serializers import (
    VisitedCitySerializer,
    NotVisitedCitySerializer,
    AddVisitedCitySerializer,
)
from city.structs import UserID
from region.models import Region
from services import logger
from services.db.visited_city_repo import get_not_visited_cities
from city.services.db import get_all_visited_cities
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
        return get_all_visited_cities(user_id)


class GetVisitedCitiesFromSubscriptions(generics.ListAPIView):
    serializer_class = VisitedCitySerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']

    def __init__(self) -> None:
        # Список ID пользователей, у которых необходимо вернуть посещённые города
        self.user_ids: list = []

        super().__init__()

    def _validate_json(self, data: str) -> None | NoReturn:
        try:
            UserID.model_validate_json(data)
        except ValidationError:
            logger.warning(
                self.request,
                '(API) An incorrect list of user IDs was received',
            )
            raise drf_exc.ParseError('Получен некорректный список идентификаторов пользователей')

    def _load_json(self, data: str) -> dict | NoReturn:
        try:
            return json.loads(data)
        except JSONDecodeError:
            logger.warning(
                self.request,
                '(API) An incorrect list of user IDs was received',
            )
            raise drf_exc.ParseError('Получен некорректный список идентификаторов пользователей')

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

        user_ids = json_data.get('id')

        if not self.request.user.is_superuser:
            # Убираем из списка ID тех пользователей, которые не разрешили подписываться на себя.
            # Вообще это нештатная ситуация, но теоритически возможная, когда пользователь запретил
            # подписываться после того, как была открыта страница с картой, но до того, как запрос пришёл на сервер.
            for user_id in user_ids:
                if self._user_has_allowed_to_subscribe_to_himself(
                    user_id
                ) and self._is_subscription_exists(user_id):
                    self.user_ids.append(user_id)
                    logger.info(
                        self.request,
                        f'(API) Successful request for a list of visited cities from subscriptions '
                        f'(from #{self.request.user.id}, to #{user_id})',
                    )
        else:
            self.user_ids = user_ids

            logger.info(
                self.request,
                f'(API) Successful request from superuser for a list of visited cities from subscriptions (user #{self.request.user.id})',
            )

        return super().get(*args, **kwargs)

    def get_queryset(self):
        # get_all_visited_cities работает с одним user_id, поэтому она вызывается
        # несколько раз и результаты собираются в один QuerySet.
        querysets = [get_all_visited_cities(user_id) for user_id in self.user_ids]
        combined_queryset = querysets[0]
        for qs in querysets[1:]:
            combined_queryset = combined_queryset.union(qs)
        return combined_queryset


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
        regions = {region.id: str(region) for region in Region.objects.all()}
        return get_not_visited_cities(self.request.user.pk, regions)


class AddVisitedCity(generics.CreateAPIView):
    serializer_class = AddVisitedCitySerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        from_page = request.data.get('from') if request.data.get('from') else 'unknown location'

        serializer = AddVisitedCitySerializer(data=request.data, context={'request': self.request})
        if not serializer.is_valid():
            logger.warning(
                self.request,
                f'(API: Add visited city) Validation in the serializer failed from {from_page}',
            )
            raise drf_exc.ValidationError(serializer.errors)

        user = request.user
        region = City.objects.get(id=serializer.validated_data['city'].id).region
        serializer.save(user=user, region=region)

        logger.info(
            self.request,
            f'(API: Add visited city) The visited city has been successfully added from {from_page}',
        )

        return Response({'status': 'success', 'city': serializer.data})
