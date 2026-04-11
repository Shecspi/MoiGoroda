from __future__ import annotations

import json
from io import BytesIO
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse
from PIL import Image
from rest_framework import status

from city.models import City
from country.models import Country


def _make_image_file(name: str = 'photo.png') -> SimpleUploadedFile:
    buffer = BytesIO()
    image = Image.new('RGB', (80, 60), color=(10, 20, 30))
    image.save(buffer, format='PNG')
    return SimpleUploadedFile(name=name, content=buffer.getvalue(), content_type='image/png')


def _json(response: object) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(getattr(response, 'content', b'').decode()))


@pytest.fixture
def client() -> Client:
    return Client()


@pytest.fixture
def country() -> Country:
    return Country.objects.create(code='RU', name='Russia')


@pytest.fixture
def city(country: Country) -> City:
    return City.objects.create(
        title='Test City',
        country=country,
        coordinate_width=55.0,
        coordinate_longitude=37.0,
        image='',
    )


@pytest.mark.django_db
@pytest.mark.integration
def test_guest_cannot_upload_standard_photo(client: Client, city: City) -> None:
    response = client.post(
        reverse('api__upload_city_standard_photo'),
        {'city_id': city.id, 'image': _make_image_file()},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
@pytest.mark.integration
def test_regular_user_forbidden(client: Client, django_user_model: type[User], city: City) -> None:
    user = django_user_model.objects.create_user(username='u', password='p')
    client.force_login(user)
    response = client.post(
        reverse('api__upload_city_standard_photo'),
        {'city_id': city.id, 'image': _make_image_file()},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.integration
def test_missing_city_id(client: Client, django_user_model: type[User]) -> None:
    admin = django_user_model.objects.create_superuser(username='a', password='p', email='a@a.a')
    client.force_login(admin)
    response = client.post(
        reverse('api__upload_city_standard_photo'),
        {'image': _make_image_file()},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.integration
def test_invalid_city_id(client: Client, django_user_model: type[User]) -> None:
    admin = django_user_model.objects.create_superuser(username='a2', password='p', email='a2@a.a')
    client.force_login(admin)
    response = client.post(
        reverse('api__upload_city_standard_photo'),
        {'city_id': 'x', 'image': _make_image_file()},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.integration
def test_city_not_found(client: Client, django_user_model: type[User]) -> None:
    admin = django_user_model.objects.create_superuser(username='a3', password='p', email='a3@a.a')
    client.force_login(admin)
    response = client.post(
        reverse('api__upload_city_standard_photo'),
        {'city_id': 999999, 'image': _make_image_file()},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.integration
def test_invalid_source_link(client: Client, django_user_model: type[User], city: City) -> None:
    admin = django_user_model.objects.create_superuser(username='a4', password='p', email='a4@a.a')
    client.force_login(admin)
    response = client.post(
        reverse('api__upload_city_standard_photo'),
        {
            'city_id': city.id,
            'image_source_link': 'ftp://example.com/x',
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.integration
@patch('city.api.standard_photo.CityStandardPhotoStorage')
def test_superuser_upload_updates_city_image(
    storage_cls: MagicMock,
    client: Client,
    django_user_model: type[User],
    city: City,
) -> None:
    storage = MagicMock()
    storage.save.return_value = 'cities/test.jpg'
    storage.url.return_value = 'https://bucket.example/cities/test.jpg'
    storage_cls.return_value = storage

    admin = django_user_model.objects.create_superuser(username='a5', password='p', email='a5@a.a')
    client.force_login(admin)
    response = client.post(
        reverse('api__upload_city_standard_photo'),
        {
            'city_id': city.id,
            'image': _make_image_file(),
            'image_source_text': 'Wiki',
            'image_source_link': 'https://example.org/src',
        },
    )
    assert response.status_code == status.HTTP_200_OK
    payload = _json(response)
    assert 'example.org' in payload['image_source_link'] or payload['image_source_link']
    city.refresh_from_db()
    assert 'bucket.example' in (city.image or '')
    assert city.image_source_text == 'Wiki'


@pytest.mark.django_db
@pytest.mark.integration
def test_metadata_only_without_image(
    client: Client, django_user_model: type[User], city: City
) -> None:
    admin = django_user_model.objects.create_superuser(username='a6', password='p', email='a6@a.a')
    client.force_login(admin)
    response = client.post(
        reverse('api__upload_city_standard_photo'),
        {
            'city_id': city.id,
            'image_source_text': 'Only text',
        },
    )
    assert response.status_code == status.HTTP_200_OK
    city.refresh_from_db()
    assert city.image_source_text == 'Only text'
