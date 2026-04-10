from __future__ import annotations

from collections.abc import Generator
from datetime import timedelta
from decimal import Decimal
from io import BytesIO
from pathlib import Path

import pytest
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from city.models import City, CityUserPhoto
from country.models import Country
from premium.models import PremiumPlan, PremiumSubscription


def _make_image_file(name: str = 'photo.png', size: tuple[int, int] = (3200, 1600)) -> SimpleUploadedFile:
    buffer = BytesIO()
    image = Image.new('RGB', size, color=(220, 120, 10))
    image.save(buffer, format='PNG')
    return SimpleUploadedFile(name=name, content=buffer.getvalue(), content_type='image/png')


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


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


@pytest.fixture
def user(django_user_model: type[User]) -> User:
    return django_user_model.objects.create_user(username='premium_user', password='pass')


@pytest.fixture
def another_user(django_user_model: type[User]) -> User:
    return django_user_model.objects.create_user(username='another_user', password='pass')


@pytest.fixture
def city() -> City:
    country = Country.objects.create(code='RU', name='Russia')
    return City.objects.create(
        title='Moscow',
        country=country,
        coordinate_width=55.751244,
        coordinate_longitude=37.618423,
        image='',
    )


@pytest.fixture
def advanced_plan() -> PremiumPlan:
    return PremiumPlan.objects.create(
        slug='advanced',
        name='Advanced',
        description='Advanced plan',
        price_month=Decimal('599.00'),
        price_year=Decimal('5990.00'),
        currency='RUB',
        is_active=True,
        sort_order=0,
    )


@pytest.fixture
def active_advanced_subscription(user: User, advanced_plan: PremiumPlan) -> PremiumSubscription:
    now = timezone.now()
    return PremiumSubscription.objects.create(
        user=user,
        plan=advanced_plan,
        billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
        status=PremiumSubscription.Status.ACTIVE,
        started_at=now,
        expires_at=now + timedelta(days=30),
        provider_payment_id='test-payment',
    )


@pytest.mark.django_db
@pytest.mark.integration
def test_guest_cannot_upload_photo(api_client: APIClient, city: City) -> None:
    response = api_client.post(
        reverse('api__upload_city_user_photo'),
        {'city_id': city.id, 'image': _make_image_file()},
        format='multipart',
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
@pytest.mark.integration
def test_upload_requires_advanced_subscription(api_client: APIClient, user: User, city: City) -> None:
    api_client.force_authenticate(user=user)
    response = api_client.post(
        reverse('api__upload_city_user_photo'),
        {'city_id': city.id, 'image': _make_image_file()},
        format='multipart',
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.integration
def test_upload_photo_success_and_default_first(
    api_client: APIClient,
    user: User,
    city: City,
    active_advanced_subscription: PremiumSubscription,
) -> None:
    api_client.force_authenticate(user=user)
    response = api_client.post(
        reverse('api__upload_city_user_photo'),
        {'city_id': city.id, 'image': _make_image_file()},
        format='multipart',
    )
    assert response.status_code == status.HTTP_201_CREATED
    photo = CityUserPhoto.objects.get(user=user, city=city)
    assert photo.is_default is True
    assert photo.position == 1


@pytest.mark.django_db
@pytest.mark.integration
def test_photos_limit_per_user_per_city(
    api_client: APIClient,
    user: User,
    city: City,
    active_advanced_subscription: PremiumSubscription,
) -> None:
    api_client.force_authenticate(user=user)
    upload_url = reverse('api__upload_city_user_photo')
    for idx in range(settings.CITY_USER_PHOTOS_LIMIT):
        response = api_client.post(
            upload_url,
            {'city_id': city.id, 'image': _make_image_file(name=f'{idx}.png')},
            format='multipart',
        )
        assert response.status_code == status.HTTP_201_CREATED

    limit_response = api_client.post(
        upload_url,
        {'city_id': city.id, 'image': _make_image_file(name='extra.png')},
        format='multipart',
    )
    assert limit_response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.django_db
@pytest.mark.integration
def test_upload_rejects_unsupported_image_format(
    api_client: APIClient,
    user: User,
    city: City,
    active_advanced_subscription: PremiumSubscription,
) -> None:
    api_client.force_authenticate(user=user)
    invalid_file = SimpleUploadedFile(
        name='photo.heic',
        content=b'not-a-valid-image',
        content_type='image/heic',
    )
    response = api_client.post(
        reverse('api__upload_city_user_photo'),
        {'city_id': city.id, 'image': invalid_file},
        format='multipart',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['image'] == ['Неподдерживаемый формат изображения']


@pytest.mark.django_db
@pytest.mark.integration
def test_upload_rejects_too_large_file(
    api_client: APIClient,
    user: User,
    city: City,
    active_advanced_subscription: PremiumSubscription,
) -> None:
    api_client.force_authenticate(user=user)

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(settings, 'CITY_USER_PHOTO_MAX_UPLOAD_MB', 1)
        monkeypatch.setattr(settings, 'CITY_USER_PHOTO_MAX_UPLOAD_BYTES', 1 * 1024 * 1024)

        too_large_content = b'a' * (settings.CITY_USER_PHOTO_MAX_UPLOAD_BYTES + 1)
        too_large_file = SimpleUploadedFile(
            name='too-large.jpg',
            content=too_large_content,
            content_type='image/jpeg',
        )
        response = api_client.post(
            reverse('api__upload_city_user_photo'),
            {'city_id': city.id, 'image': too_large_file},
            format='multipart',
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == 'Размер файла превышает допустимый лимит 1 МБ'


@pytest.mark.django_db
@pytest.mark.integration
def test_owner_only_access_to_photo_content(
    api_client: APIClient,
    user: User,
    another_user: User,
    city: City,
    active_advanced_subscription: PremiumSubscription,
) -> None:
    photo = CityUserPhoto.objects.create(
        user=user,
        city=city,
        image=_make_image_file(),
        is_default=True,
        position=1,
    )
    api_client.force_authenticate(user=another_user)
    response = api_client.get(reverse('api__city_user_photo_content', kwargs={'photo_id': photo.id}))
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.integration
def test_set_default_and_delete_photo(
    api_client: APIClient,
    user: User,
    city: City,
    active_advanced_subscription: PremiumSubscription,
) -> None:
    photo1 = CityUserPhoto.objects.create(
        user=user,
        city=city,
        image=_make_image_file(name='1.png'),
        is_default=True,
        position=1,
    )
    photo2 = CityUserPhoto.objects.create(
        user=user,
        city=city,
        image=_make_image_file(name='2.png'),
        is_default=False,
        position=2,
    )

    api_client.force_authenticate(user=user)
    set_default_response = api_client.post(
        reverse('api__set_default_city_user_photo', kwargs={'photo_id': photo2.id})
    )
    assert set_default_response.status_code == status.HTTP_200_OK
    photo1.refresh_from_db()
    photo2.refresh_from_db()
    assert photo1.is_default is False
    assert photo2.is_default is True

    delete_response = api_client.delete(
        reverse('api__city_user_photo_content', kwargs={'photo_id': photo2.id})
    )
    assert delete_response.status_code == status.HTTP_200_OK
    delete_payload = delete_response.json()
    assert delete_payload['status'] == 'success'
    assert delete_payload['default_photo_id'] == str(photo1.id)
    photo1.refresh_from_db()
    assert photo1.is_default is True


@pytest.mark.django_db
@pytest.mark.integration
def test_delete_last_photo_returns_null_default_id(
    api_client: APIClient,
    user: User,
    city: City,
    active_advanced_subscription: PremiumSubscription,
) -> None:
    photo = CityUserPhoto.objects.create(
        user=user,
        city=city,
        image=_make_image_file(name='only.png'),
        is_default=True,
        position=1,
    )
    api_client.force_authenticate(user=user)
    delete_response = api_client.delete(
        reverse('api__city_user_photo_content', kwargs={'photo_id': photo.id})
    )
    assert delete_response.status_code == status.HTTP_200_OK
    assert delete_response.json() == {'status': 'success', 'default_photo_id': None}
    assert not CityUserPhoto.objects.filter(id=photo.id).exists()


@pytest.mark.django_db
@pytest.mark.integration
def test_delete_middle_photo_reorders_positions_without_conflict(
    api_client: APIClient,
    user: User,
    city: City,
    active_advanced_subscription: PremiumSubscription,
) -> None:
    photo1 = CityUserPhoto.objects.create(
        user=user,
        city=city,
        image=_make_image_file(name='1.png'),
        is_default=True,
        position=1,
    )
    photo2 = CityUserPhoto.objects.create(
        user=user,
        city=city,
        image=_make_image_file(name='2.png'),
        is_default=False,
        position=2,
    )
    photo3 = CityUserPhoto.objects.create(
        user=user,
        city=city,
        image=_make_image_file(name='3.png'),
        is_default=False,
        position=3,
    )

    api_client.force_authenticate(user=user)
    delete_response = api_client.delete(
        reverse('api__city_user_photo_content', kwargs={'photo_id': photo2.id})
    )
    assert delete_response.status_code == status.HTTP_200_OK
    assert not CityUserPhoto.objects.filter(id=photo2.id).exists()

    photo1.refresh_from_db()
    photo3.refresh_from_db()
    assert photo1.position == 1
    assert photo3.position == 2
    assert photo1.is_default is True
