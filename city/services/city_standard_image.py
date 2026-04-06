"""
Путь к стандартному изображению города в объектном хранилище (S3).

Если у региона задан код ISO3166: {код страны}/{сегмент региона}/{транслит названия}.jpg
Сегмент региона — без префикса страны: в БД может быть ``RU-AL``, в пути папка ``AL``,
так как уровень страны уже задан первым сегментом.

Иначе (нет региона или пустой код): {код страны}/{транслит названия}.jpg

Примеры: RU/AL/barnaul.jpg, RU/AST/astrakhan.jpg, DE/berlin.jpg
"""

from __future__ import annotations

import re

from city.models import City

_FILENAME_FORBIDDEN = re.compile(r'[/\\:*?"<>|]+')
_MULTI_HYPHEN = re.compile(r'-+')

# Транслитерация кириллицы (рус.) в латиницу, близко к практическому написанию топонимов.
_CYR_TO_LAT: dict[str, str] = {
    'а': 'a',
    'б': 'b',
    'в': 'v',
    'г': 'g',
    'д': 'd',
    'е': 'e',
    'ё': 'yo',
    'ж': 'zh',
    'з': 'z',
    'и': 'i',
    'й': 'y',
    'к': 'k',
    'л': 'l',
    'м': 'm',
    'н': 'n',
    'о': 'o',
    'п': 'p',
    'р': 'r',
    'с': 's',
    'т': 't',
    'у': 'u',
    'ф': 'f',
    'х': 'kh',
    'ц': 'ts',
    'ч': 'ch',
    'ш': 'sh',
    'щ': 'shch',
    'ъ': '',
    'ы': 'y',
    'ь': '',
    'э': 'e',
    'ю': 'yu',
    'я': 'ya',
}


def transliterate_ru_city_title_to_latin_slug(title: str) -> str:
    """
    Название города в латинской транскрипции для имени файла: строчные буквы, дефисы вместо пробелов.
    """
    parts: list[str] = []

    for ch in title.strip().lower():
        if ch in _CYR_TO_LAT:
            parts.append(_CYR_TO_LAT[ch])
        elif ch.isascii() and ch.isalnum():
            parts.append(ch)
        elif ch in (' ', '-', '_'):
            parts.append('-')

    raw = ''.join(parts)
    raw = _MULTI_HYPHEN.sub('-', raw)

    return raw.strip('-')


def sanitize_city_image_basename(title: str, city_id: int) -> str:
    """Имя файла без расширения: транслит названия города, безопасные символы."""
    s = transliterate_ru_city_title_to_latin_slug(title)
    s = _FILENAME_FORBIDDEN.sub('', s)
    s = _MULTI_HYPHEN.sub('-', s).strip('-')

    if not s:
        s = f'city-{city_id}'

    return s[:200]


def region_folder_segment(country_code: str, iso3166: str) -> str | None:
    """
    Часть пути для региона: убирает префикс «код страны-», если он совпадает с ``country_code``.

    ``RU-AL`` при стране ``RU`` → ``AL``; ``AST`` или ``DE-BE`` без совпадения с страной — без изменений.
    """
    raw = iso3166.strip()

    if not raw:
        return None

    cc = country_code.upper()
    prefix = f'{cc}-'

    if raw.upper().startswith(prefix):
        rest = raw[len(prefix) :].strip()

        return rest if rest else None

    return raw


def build_standard_city_image_storage_key(city: City, extension: str) -> str:
    """
    Ключ объекта в бакете. При непустом ISO3166 у региона — вложенная папка региона, иначе — только страна.
    """
    country_code = city.country.code.upper()

    ext = extension.lower().lstrip('.')
    if ext not in ('jpg', 'jpeg', 'png', 'webp'):
        ext = 'jpg'
    if ext == 'jpeg':
        ext = 'jpg'

    base = sanitize_city_image_basename(city.title, city.pk)

    region_segment: str | None = None

    if city.region_id and city.region is not None:
        raw_iso = city.region.iso3166
        region_segment = region_folder_segment(country_code, raw_iso)

    if region_segment:
        return f'{country_code}/{region_segment}/{base}.{ext}'

    return f'{country_code}/{base}.{ext}'
