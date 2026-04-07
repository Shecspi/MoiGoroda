"""
API для пользовательских фотографий городов.

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import mimetypes
from http import HTTPStatus
from typing import Any, cast
from uuid import UUID

from django.contrib.auth.models import User
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from django.db.models import F, Max
from django.http import FileResponse, HttpResponseBase
from dmr import Controller, ResponseSpec, modify, validate
from dmr.files import FileResponseSpec
from dmr.plugins.msgspec import MsgspecSerializer
from dmr.renderers import FileRenderer
import msgspec

from city.models import City, CityUserPhoto
from city.serializers import CityUserPhotoSerializer
from city.services.photo_processing import compress_city_photo
from premium.services.access import has_advanced_premium


class UploadCityUserPhotoBody(msgspec.Struct):
    city_id: int


class CityUserPhotosController(Controller[MsgspecSerializer]):
    @modify(
        status_code=HTTPStatus.OK,
        extra_responses=[
            ResponseSpec(dict[str, str], status_code=HTTPStatus.BAD_REQUEST),
            ResponseSpec(dict[str, str], status_code=HTTPStatus.FORBIDDEN),
            ResponseSpec(dict[str, str], status_code=HTTPStatus.UNAUTHORIZED),
        ],
        tags=['Пользовательские фото городов'],
    )
    def get(self) -> Any:
        if not self.request.user.is_authenticated:
            return self.to_response(
                raw_data={'detail': 'Требуется авторизация'},
                status_code=HTTPStatus.UNAUTHORIZED,
            )

        assert isinstance(self.request.user, User)

        if not has_advanced_premium(self.request.user):
            return self.to_response(
                raw_data={'detail': 'Функция доступна только для подписки advanced'},
                status_code=HTTPStatus.FORBIDDEN,
            )

        city_id = self.request.GET.get('city_id')
        if not city_id:
            return self.to_response(
                raw_data={'detail': 'Параметр city_id является обязательным'},
                status_code=HTTPStatus.BAD_REQUEST,
            )

        try:
            city_id_int = int(city_id)
        except ValueError:
            return self.to_response(
                raw_data={'detail': 'city_id должен быть числом'},
                status_code=HTTPStatus.BAD_REQUEST,
            )

        photos = CityUserPhoto.objects.filter(user=self.request.user, city_id=city_id_int).order_by(
            '-is_default', 'position', '-created_at'
        )
        serializer = CityUserPhotoSerializer(photos, many=True, context={'request': self.request})
        return self.to_response(
            raw_data={'photos': serializer.data},
            status_code=HTTPStatus.OK,
        )


class UploadCityUserPhotoController(Controller[MsgspecSerializer]):
    @modify(
        status_code=HTTPStatus.CREATED,
        extra_responses=[
            ResponseSpec(dict[str, Any], status_code=HTTPStatus.BAD_REQUEST),
            ResponseSpec(dict[str, str], status_code=HTTPStatus.FORBIDDEN),
            ResponseSpec(dict[str, str], status_code=HTTPStatus.UNAUTHORIZED),
            ResponseSpec(dict[str, str], status_code=HTTPStatus.NOT_FOUND),
            ResponseSpec(dict[str, str], status_code=HTTPStatus.CONFLICT),
        ],
        tags=['Пользовательские фото городов'],
    )
    def post(self) -> Any:
        if not self.request.user.is_authenticated:
            return self.to_response(
                raw_data={'detail': 'Требуется авторизация'},
                status_code=HTTPStatus.UNAUTHORIZED,
            )

        assert isinstance(self.request.user, User)

        if not has_advanced_premium(self.request.user):
            return self.to_response(
                raw_data={'detail': 'Функция доступна только для подписки advanced'},
                status_code=HTTPStatus.FORBIDDEN,
            )

        city_id = self.request.POST.get('city_id')
        if not city_id:
            return self.to_response(
                raw_data={'detail': 'Параметр city_id является обязательным'},
                status_code=HTTPStatus.BAD_REQUEST,
            )

        image = self.request.FILES.get('image')

        try:
            payload = UploadCityUserPhotoBody(int(city_id))
        except (TypeError, ValueError):
            return self.to_response(
                raw_data={'city_id': ['A valid integer is required.']},
                status_code=HTTPStatus.BAD_REQUEST,
            )

        if payload.city_id <= 0:
            return self.to_response(
                raw_data={'city_id': ['This field is required.']},
                status_code=HTTPStatus.BAD_REQUEST,
            )

        if not isinstance(image, UploadedFile):
            return self.to_response(
                raw_data={'image': ['No file was submitted.']},
                status_code=HTTPStatus.BAD_REQUEST,
            )

        try:
            city = City.objects.get(pk=payload.city_id)
        except City.DoesNotExist:
            return self.to_response(
                raw_data={'detail': 'Город не найден'},
                status_code=HTTPStatus.NOT_FOUND,
            )

        with transaction.atomic():
            user_city_qs = CityUserPhoto.objects.select_for_update().filter(
                user=self.request.user, city=city
            )

            if user_city_qs.count() >= 5:
                return self.to_response(
                    raw_data={'detail': 'Можно загрузить не более 5 фотографий для одного города'},
                    status_code=HTTPStatus.CONFLICT,
                )

            max_position = user_city_qs.aggregate(max_position=Max('position'))['max_position'] or 0

            try:
                compressed_file = compress_city_photo(image)
            except ValueError:
                return self.to_response(
                    raw_data={'image': ['Неподдерживаемый формат изображения']},
                    status_code=HTTPStatus.BAD_REQUEST,
                )

            photo = CityUserPhoto.objects.create(
                user=self.request.user,
                city=city,
                image=compressed_file,
                is_default=not user_city_qs.exists(),
                position=max_position + 1,
            )

        response_serializer = CityUserPhotoSerializer(photo, context={'request': self.request})

        return self.to_response(
            raw_data={'photo': response_serializer.data},
            status_code=HTTPStatus.CREATED,
        )


class CityUserPhotoController(Controller[MsgspecSerializer]):
    @validate(
        FileResponseSpec(),
        ResponseSpec(dict[str, str], status_code=HTTPStatus.UNAUTHORIZED),
        ResponseSpec(dict[str, str], status_code=HTTPStatus.NOT_FOUND),
        renderers=[FileRenderer()],
        tags=['Пользовательские фото городов'],
    )
    def get(self) -> HttpResponseBase:
        if not self.request.user.is_authenticated:
            return self.to_response(
                raw_data={'detail': 'Требуется авторизация'},
                status_code=HTTPStatus.UNAUTHORIZED,
            )

        assert isinstance(self.request.user, User)

        photo = CityUserPhoto.objects.filter(
            id=self.kwargs['photo_id'], user=self.request.user
        ).first()

        if photo is None:
            return self.to_response(
                raw_data={'detail': 'Фотография не найдена'},
                status_code=HTTPStatus.NOT_FOUND,
            )

        content_type = mimetypes.guess_type(photo.image.name)[0] or 'application/octet-stream'

        return FileResponse(photo.image.open('rb'), content_type=content_type)

    @modify(
        status_code=HTTPStatus.OK,
        extra_responses=[
            ResponseSpec(dict[str, str], status_code=HTTPStatus.UNAUTHORIZED),
            ResponseSpec(dict[str, str], status_code=HTTPStatus.FORBIDDEN),
            ResponseSpec(dict[str, str], status_code=HTTPStatus.NOT_FOUND),
        ],
        tags=['Пользовательские фото городов'],
    )
    def delete(self) -> Any:
        photo_id = cast(UUID, self.kwargs['photo_id'])

        if not self.request.user.is_authenticated:
            return self.to_response(
                raw_data={'detail': 'Требуется авторизация'},
                status_code=HTTPStatus.UNAUTHORIZED,
            )

        assert isinstance(self.request.user, User)
        if not has_advanced_premium(self.request.user):
            return self.to_response(
                raw_data={'detail': 'Функция доступна только для подписки advanced'},
                status_code=HTTPStatus.FORBIDDEN,
            )

        image_name: str | None = None
        image_storage = None

        with transaction.atomic():
            photo = (
                CityUserPhoto.objects.select_for_update()
                .filter(id=photo_id, user=self.request.user)
                .select_related('city')
                .first()
            )
            if photo is None:
                return self.to_response(
                    raw_data={'detail': 'Фотография не найдена'},
                    status_code=HTTPStatus.NOT_FOUND,
                )

            city_id = photo.city_id
            image_name = photo.image.name
            image_storage = photo.image.storage
            photo.delete()

            photos_qs = (
                CityUserPhoto.objects.select_for_update()
                .filter(user=self.request.user, city_id=city_id)
                .order_by('-is_default', 'position', '-created_at')
            )
            photos_qs.update(position=F('position') + 100)
            photos = list(photos_qs)
            has_default = False

            for idx, item in enumerate(photos, start=1):
                item.position = idx
                if item.is_default and not has_default:
                    has_default = True
                elif item.is_default and has_default:
                    item.is_default = False
                item.save(update_fields=['position', 'is_default', 'updated_at'])

            if photos and not has_default:
                first_photo = photos[0]
                first_photo.is_default = True
                first_photo.save(update_fields=['is_default', 'updated_at'])

            default_photo_id: str | None = None

            for item in photos:
                if item.is_default:
                    default_photo_id = str(item.id)
                    break

            if image_name and image_storage is not None:
                transaction.on_commit(lambda: image_storage.delete(image_name))

        return self.to_response(
            raw_data={'status': 'success', 'default_photo_id': default_photo_id},
            status_code=HTTPStatus.OK,
        )


class SetDefaultCityUserPhotoController(Controller[MsgspecSerializer]):
    @modify(
        status_code=HTTPStatus.OK,
        extra_responses=[
            ResponseSpec(dict[str, str], status_code=HTTPStatus.UNAUTHORIZED),
            ResponseSpec(dict[str, str], status_code=HTTPStatus.FORBIDDEN),
            ResponseSpec(dict[str, str], status_code=HTTPStatus.NOT_FOUND),
        ],
        tags=['Пользовательские фото городов'],
    )
    def post(self) -> Any:
        photo_id = cast(UUID, self.kwargs['photo_id'])

        if not self.request.user.is_authenticated:
            return self.to_response(
                raw_data={'detail': 'Требуется авторизация'},
                status_code=HTTPStatus.UNAUTHORIZED,
            )

        assert isinstance(self.request.user, User)
        if not has_advanced_premium(self.request.user):
            return self.to_response(
                raw_data={'detail': 'Функция доступна только для подписки advanced'},
                status_code=HTTPStatus.FORBIDDEN,
            )

        with transaction.atomic():
            photo = (
                CityUserPhoto.objects.select_for_update()
                .filter(id=photo_id, user=self.request.user)
                .select_related('city')
                .first()
            )
            if photo is None:
                return self.to_response(
                    raw_data={'detail': 'Фотография не найдена'},
                    status_code=HTTPStatus.NOT_FOUND,
                )

            CityUserPhoto.objects.select_for_update().filter(
                user=self.request.user,
                city=photo.city,
                is_default=True,
            ).update(is_default=False)
            photo.is_default = True
            photo.save(update_fields=['is_default', 'updated_at'])

        return self.to_response(raw_data={'status': 'success'}, status_code=HTTPStatus.OK)
