"""
API обновления стандартного изображения города (только суперпользователь).

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from http import HTTPStatus
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from dmr import Controller, ResponseSpec, modify
from dmr.plugins.msgspec import MsgspecSerializer

from MoiGoroda.storages import CityStandardPhotoStorage

from city.models import City
from city.services.city_standard_image import build_standard_city_image_storage_key
from city.services.photo_processing import compress_city_photo


def _append_cache_bust_query(url: str) -> str:
    """
    Меняет строку URL для обхода кеша браузера/CDN при той же позиции объекта в S3.
    Параметр ``v`` обычно игнорируется при выдаче объекта из бакета.
    """
    token = str(int(timezone.now().timestamp() * 1000))
    parsed = urlparse(url)
    pairs = dict(parse_qsl(parsed.query, keep_blank_values=True))
    pairs['v'] = token

    return urlunparse(parsed._replace(query=urlencode(pairs)))


class UploadCityStandardPhotoController(Controller[MsgspecSerializer]):
    @modify(
        status_code=HTTPStatus.OK,
        extra_responses=[
            ResponseSpec(dict[str, Any], status_code=HTTPStatus.BAD_REQUEST),
            ResponseSpec(dict[str, str], status_code=HTTPStatus.FORBIDDEN),
            ResponseSpec(dict[str, str], status_code=HTTPStatus.UNAUTHORIZED),
            ResponseSpec(dict[str, str], status_code=HTTPStatus.NOT_FOUND),
        ],
        tags=['Стандартное фото города'],
    )
    def post(self) -> Any:
        if not self.request.user.is_authenticated:
            return self.to_response(
                raw_data={'detail': 'Требуется авторизация'},
                status_code=HTTPStatus.UNAUTHORIZED,
            )

        assert isinstance(self.request.user, User)

        if not self.request.user.is_superuser:
            return self.to_response(
                raw_data={'detail': 'Доступно только суперпользователю'},
                status_code=HTTPStatus.FORBIDDEN,
            )

        city_id_raw = self.request.POST.get('city_id')
        image_source_text = (self.request.POST.get('image_source_text') or '').strip()
        image_source_link_raw = (self.request.POST.get('image_source_link') or '').strip()

        if not city_id_raw:
            return self.to_response(
                raw_data={'city_id': ['Обязательное поле']},
                status_code=HTTPStatus.BAD_REQUEST,
            )

        try:
            city_id = int(city_id_raw)
        except (TypeError, ValueError):
            return self.to_response(
                raw_data={'city_id': ['Некорректное значение']},
                status_code=HTTPStatus.BAD_REQUEST,
            )

        image = self.request.FILES.get('image')

        image_source_link = image_source_link_raw or None
        if image_source_link:
            parsed = urlparse(image_source_link)
            if parsed.scheme not in ('http', 'https') or not parsed.netloc:
                return self.to_response(
                    raw_data={'image_source_link': ['Укажите корректный URL (http или https)']},
                    status_code=HTTPStatus.BAD_REQUEST,
                )

        try:
            city = City.objects.select_related('country', 'region').get(pk=city_id)
        except City.DoesNotExist:
            return self.to_response(
                raw_data={'detail': 'Город не найден'},
                status_code=HTTPStatus.NOT_FOUND,
            )

        absolute_url: str | None = None

        if image is not None:
            if not isinstance(image, UploadedFile):
                return self.to_response(
                    raw_data={'image': ['Некорректный файл']},
                    status_code=HTTPStatus.BAD_REQUEST,
                )

            try:
                compressed = compress_city_photo(image)
            except ValueError as exc:
                message = str(exc)
                if message == 'Слишком большое изображение':
                    return self.to_response(
                        raw_data={'image': [message]},
                        status_code=HTTPStatus.BAD_REQUEST,
                    )
                return self.to_response(
                    raw_data={'image': ['Неподдерживаемый формат изображения']},
                    status_code=HTTPStatus.BAD_REQUEST,
                )

            try:
                storage_key = build_standard_city_image_storage_key(city, 'jpg')
            except ValueError as exc:
                return self.to_response(
                    raw_data={'detail': str(exc)},
                    status_code=HTTPStatus.BAD_REQUEST,
                )

            storage = CityStandardPhotoStorage()
            saved_name = storage.save(storage_key, compressed)
            public_url = storage.url(saved_name)

            if public_url.startswith(('http://', 'https://')):
                absolute_url = public_url
            else:
                absolute_url = self.request.build_absolute_uri(public_url)

            absolute_url = _append_cache_bust_query(absolute_url)

        with transaction.atomic():
            city_locked = City.objects.select_for_update().get(pk=city.pk)

            if absolute_url is not None:
                city_locked.image = absolute_url

            city_locked.image_source_text = image_source_text or None
            city_locked.image_source_link = image_source_link
            city_locked.save(update_fields=['image', 'image_source_text', 'image_source_link'])

        return self.to_response(
            raw_data={
                'image': city_locked.image or '',
                'image_source_text': city_locked.image_source_text or '',
                'image_source_link': city_locked.image_source_link or '',
            },
            status_code=HTTPStatus.OK,
        )
