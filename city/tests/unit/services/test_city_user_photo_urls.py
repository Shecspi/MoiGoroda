from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile

from city.models import City, CityUserPhoto
from city.services.city_user_photo_urls import (
    attach_default_city_user_photo_presigned_urls,
    city_user_photo_file_url,
)
from country.models import Country


@pytest.fixture(autouse=True)
def use_local_storage_for_city_photos(
    tmp_path: Path,
) -> Generator[FileSystemStorage, None, None]:
    storage = FileSystemStorage(location=tmp_path, base_url='/media/')
    image_field = CityUserPhoto._meta.get_field('image')
    original_storage = image_field.storage
    image_field.storage = storage
    try:
        yield storage
    finally:
        image_field.storage = original_storage


@pytest.mark.django_db
@pytest.mark.unit
def test_city_user_photo_file_url_uses_storage_url() -> None:
    user = User.objects.create_user(username='u', password='p')
    country = Country.objects.create(code='RU', name='Russia')
    city = City.objects.create(
        title='X',
        country=country,
        coordinate_width=1.0,
        coordinate_longitude=1.0,
        image='',
    )
    photo = CityUserPhoto.objects.create(
        user=user,
        city=city,
        image=SimpleUploadedFile('f.jpg', b'x', content_type='image/jpeg'),
        is_default=True,
        position=1,
    )
    url = city_user_photo_file_url(photo)
    assert '.jpg' in url
    assert url.startswith('http') or url.startswith('/')


@pytest.mark.django_db
@pytest.mark.unit
def test_attach_presigned_urls_skips_when_no_annotation() -> None:
    user = User.objects.create_user(username='u2', password='p')
    items: list[dict[str, Any]] = [{'id': 1}]
    attach_default_city_user_photo_presigned_urls(items, user.id)
    assert 'default_city_user_photo_url' not in items[0]


@pytest.mark.django_db
@pytest.mark.unit
def test_attach_presigned_urls_dict_and_model() -> None:
    user = User.objects.create_user(username='u3', password='p')
    other = User.objects.create_user(username='u4', password='p')
    country = Country.objects.create(code='RU', name='Russia')
    city = City.objects.create(
        title='Y',
        country=country,
        coordinate_width=1.0,
        coordinate_longitude=1.0,
        image='',
    )
    photo = CityUserPhoto.objects.create(
        user=user,
        city=city,
        image=SimpleUploadedFile('a.jpg', b'x', content_type='image/jpeg'),
        is_default=True,
        position=1,
    )

    class Row:
        def __init__(self) -> None:
            self.default_city_user_photo_id = photo.id

    row = Row()
    dct = {'default_city_user_photo_id': str(photo.id)}

    attach_default_city_user_photo_presigned_urls([row, dct], user.id)
    assert '.jpg' in getattr(row, 'default_city_user_photo_url', '')
    assert '.jpg' in dct['default_city_user_photo_url']

    # Чужой user_id — не подставляем URL по чужому файлу
    row2 = Row()
    attach_default_city_user_photo_presigned_urls([row2], other.id)
    assert not hasattr(row2, 'default_city_user_photo_url')
