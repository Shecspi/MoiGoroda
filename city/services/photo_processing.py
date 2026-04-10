from __future__ import annotations

from io import BytesIO
from typing import Any

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from PIL import Image, ImageOps, UnidentifiedImageError
from PIL.Image import DecompressionBombError

try:
    import pillow_heif  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover - fallback for environments without optional dependency
    pillow_heif = None
else:
    pillow_heif.register_heif_opener()

ALLOWED_IMAGE_FORMATS = {'JPEG', 'JPG', 'PNG', 'WEBP'}
MAX_IMAGE_SIDE = 1920
JPEG_QUALITY = 82


def compress_city_photo(uploaded_file: UploadedFile) -> ContentFile[Any]:
    Image.MAX_IMAGE_PIXELS = settings.CITY_USER_PHOTO_MAX_PIXELS

    try:
        image = Image.open(uploaded_file)
    except (DecompressionBombError, UnidentifiedImageError, OSError) as exc:
        raise ValueError('Неподдерживаемый формат изображения') from exc

    width, height = image.size
    if width <= 0 or height <= 0:
        raise ValueError('Неподдерживаемый формат изображения')

    if width * height > settings.CITY_USER_PHOTO_MAX_PIXELS:
        raise ValueError('Слишком большое изображение')

    normalized = ImageOps.exif_transpose(image)
    image_format = (normalized.format or '').upper()

    if image_format not in ALLOWED_IMAGE_FORMATS:
        image_format = 'JPEG'

    if normalized.mode not in ('RGB', 'L'):
        normalized = normalized.convert('RGB')

    normalized.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE))
    buffer = BytesIO()
    normalized.save(buffer, format='JPEG', quality=JPEG_QUALITY, optimize=True)

    original_name = uploaded_file.name or 'image'
    stem = original_name.rsplit('.', 1)[0]

    return ContentFile(buffer.getvalue(), name=f'{stem}.jpg')
