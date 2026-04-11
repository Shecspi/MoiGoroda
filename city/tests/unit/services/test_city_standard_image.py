"""Тесты пути стандартного изображения города в S3."""

from unittest.mock import Mock

import pytest

from city.services.city_standard_image import (
    build_standard_city_image_storage_key,
    region_folder_segment,
    sanitize_city_image_basename,
    transliterate_ru_city_title_to_latin_slug,
)

pytestmark = pytest.mark.django_db


def test_transliterate_ru_city_title_to_latin_slug() -> None:
    assert transliterate_ru_city_title_to_latin_slug('Астрахань') == 'astrakhan'
    assert transliterate_ru_city_title_to_latin_slug('Санкт-Петербург') == 'sankt-peterburg'


def test_sanitize_city_image_basename_strips_forbidden() -> None:
    assert sanitize_city_image_basename('  Астрахань  ', 1) == 'astrakhan'
    assert sanitize_city_image_basename('a/b', 99) == 'ab'


def test_sanitize_city_image_basename_fallback_id() -> None:
    assert sanitize_city_image_basename('///', 42) == 'city-42'


def test_region_folder_segment_strips_country_prefix() -> None:
    assert region_folder_segment('RU', 'RU-AL') == 'AL'
    assert region_folder_segment('ru', 'ru-BA') == 'BA'
    assert region_folder_segment('DE', 'DE-BE') == 'BE'


def test_region_folder_segment_unchanged_if_no_prefix() -> None:
    assert region_folder_segment('RU', 'AST') == 'AST'
    assert region_folder_segment('RU', 'RUSS') == 'RUSS'


def test_build_standard_city_image_storage_key_ru_ast() -> None:
    country = Mock(code='ru')
    region = Mock(iso3166='AST')
    city = Mock(
        pk=1,
        title='Астрахань',
        country=country,
        region=region,
        region_id=1,
    )

    assert build_standard_city_image_storage_key(city, 'jpg') == 'RU/AST/astrakhan.jpg'


def test_build_standard_city_image_storage_key_ru_al() -> None:
    country = Mock(code='ru')
    region = Mock(iso3166='RU-AL')
    city = Mock(
        pk=1,
        title='Барнаул',
        country=country,
        region=region,
        region_id=1,
    )

    assert build_standard_city_image_storage_key(city, 'jpg') == 'RU/AL/barnaul.jpg'


def test_build_standard_city_image_storage_key_without_region() -> None:
    country = Mock(code='de')
    city = Mock(
        pk=1,
        title='Berlin',
        country=country,
        region=None,
        region_id=None,
    )

    assert build_standard_city_image_storage_key(city, 'jpg') == 'DE/berlin.jpg'


def test_build_standard_city_image_storage_key_empty_region_iso() -> None:
    country = Mock(code='ru')
    region = Mock(iso3166='   ')
    city = Mock(
        pk=1,
        title='Астрахань',
        country=country,
        region=region,
        region_id=1,
    )

    assert build_standard_city_image_storage_key(city, 'jpg') == 'RU/astrakhan.jpg'
