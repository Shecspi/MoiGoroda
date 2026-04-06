"""
Прямые URL к файлам пользовательских фото (для приватного S3 — presigned).

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from __future__ import annotations

from typing import Any, Iterable
from uuid import UUID

from city.models import CityUserPhoto


def city_user_photo_file_url(photo: CityUserPhoto) -> str:
    """
    Возвращает URL файла изображения в бэкенде хранения.

    Для приватного бакета S3 с ``querystring_auth`` это presigned GET-ссылка
    с ограниченным сроком действия.

    Args:
        photo: Запись пользовательского фото с заполненным полем ``image``.

    Returns:
        Строка URL, пригодная для ``src``/``href`` в разметке или для API.
    """
    return str(photo.image.url)


def attach_default_city_user_photo_presigned_urls(items: Iterable[Any], user_id: int) -> None:
    """
    Подставляет в элементы списка прямой URL дефолтного фото пользователя по городу.

    Ожидается, что у каждого элемента уже есть аннотация
    ``default_city_user_photo_id`` (UUID фото по умолчанию для пары пользователь–город).
    В объект добавляется атрибут/ключ ``default_city_user_photo_url`` с тем же URL,
    что даёт хранилище для ``CityUserPhoto.image`` (presigned при приватном S3).

    Идентификаторы собираются в первом проходе, затем выполняется один запрос к БД
    на все фото страницы, во втором проходе URL раздаются по элементам.

    Args:
        items: Строки текущей страницы списка: экземпляры моделей или словари из ``QuerySet.values()``.
        user_id: Владелец фото; загружаются только записи ``CityUserPhoto`` с этим ``user_id``,
            чтобы не отдавать чужие файлы по id из аннотации.

    Side effects:
        Мутирует переданные объекты/словари, добавляя ``default_city_user_photo_url``.
    """
    collected: list[Any] = list(items)
    ids: list[UUID] = []

    for item in collected:
        pid = _get_default_city_user_photo_id(item)

        if pid is None:
            continue

        if isinstance(pid, UUID):
            ids.append(pid)
        else:
            ids.append(UUID(str(pid)))

    if not ids:
        return

    photos = CityUserPhoto.objects.filter(id__in=ids, user_id=user_id).only('id', 'image')
    url_by_id = {str(photo.pk): city_user_photo_file_url(photo) for photo in photos}

    for item in collected:
        pid = _get_default_city_user_photo_id(item)

        if pid is None:
            continue

        key = str(pid)
        url = url_by_id.get(key)

        if url:
            _set_default_city_user_photo_url(item, url)


def _get_default_city_user_photo_id(item: Any) -> UUID | str | None:
    """
    Читает аннотированный идентификатор дефолтного фото из элемента списка.

    Args:
        item: Словарь (результат ``.values()``) или модель с атрибутом
            ``default_city_user_photo_id``.

    Returns:
        UUID или строковое представление, либо ``None``, если фото не задано.
    """
    if isinstance(item, dict):
        return item.get('default_city_user_photo_id')
    return getattr(item, 'default_city_user_photo_id', None)


def _set_default_city_user_photo_url(item: Any, url: str) -> None:
    """
    Записывает готовый URL превью в элемент списка.

    Args:
        item: Тот же тип, что в ``attach_default_city_user_photo_presigned_urls``.
        url: Строка URL для подстановки в шаблон (например presigned S3).

    Side effects:
        У словаря устанавливает ключ ``default_city_user_photo_url``,
        у модели — атрибут с тем же именем.
    """
    if isinstance(item, dict):
        item['default_city_user_photo_url'] = url
    else:
        setattr(item, 'default_city_user_photo_url', url)
