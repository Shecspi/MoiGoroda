from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from storages.backends.s3boto3 import S3Boto3Storage  # type: ignore[import-untyped]
from typing import Any


class UsersCityPhotoStorage(S3Boto3Storage):  # type: ignore[misc]
    querystring_auth = True
    default_acl = None
    file_overwrite = False

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault('bucket_name', settings.AWS_USERS_CITY_PHOTOS_BUCKET_NAME)
        kwargs.setdefault('region_name', settings.AWS_USERS_CITY_PHOTOS_REGION_NAME)
        kwargs.setdefault('querystring_expire', settings.AWS_USERS_CITY_PHOTOS_URL_EXPIRE_SECONDS)

        if not kwargs.get('bucket_name'):
            raise ImproperlyConfigured(
                'Задайте AWS_USERS_CITY_PHOTOS_BUCKET_NAME в окружении (см. .env.example).'
            )

        super().__init__(**kwargs)


class CityStandardPhotoStorage(S3Boto3Storage):  # type: ignore[misc]
    """
    Бакет стандартных изображений городов.

    URL без подписи: в ``City.image`` хранится постоянная строка, в отличие от
    ``UsersCityPhotoStorage``, где ссылка обновляется при каждом обращении к полю ``ImageField``.
    """

    querystring_auth = False
    default_acl = None
    file_overwrite = True

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault('bucket_name', settings.AWS_STANDARD_CITY_PHOTOS_BUCKET_NAME)
        kwargs.setdefault('region_name', settings.AWS_STANDARD_CITY_PHOTOS_REGION_NAME)
        kwargs.setdefault(
            'querystring_expire', settings.AWS_STANDARD_CITY_PHOTOS_URL_EXPIRE_SECONDS
        )

        if not kwargs.get('bucket_name'):
            raise ImproperlyConfigured(
                'Задайте AWS_STANDARD_CITY_PHOTOS_BUCKET_NAME в окружении (см. .env.example).'
            )

        super().__init__(**kwargs)
