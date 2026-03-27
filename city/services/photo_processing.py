from __future__ import annotations

from io import BytesIO

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from PIL import Image, ImageOps

ALLOWED_IMAGE_FORMATS = {'JPEG', 'JPG', 'PNG', 'WEBP'}
MAX_IMAGE_SIDE = 1920
JPEG_QUALITY = 82


def compress_city_photo(uploaded_file: UploadedFile) -> ContentFile:
    image = Image.open(uploaded_file)
    normalized = ImageOps.exif_transpose(image)
    image_format = (normalized.format or '').upper()

    if image_format not in ALLOWED_IMAGE_FORMATS:
        image_format = 'JPEG'

    if normalized.mode not in ('RGB', 'L'):
        normalized = normalized.convert('RGB')

    normalized.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE))
    buffer = BytesIO()
    normalized.save(buffer, format='JPEG', quality=JPEG_QUALITY, optimize=True)

    return ContentFile(buffer.getvalue(), name=f'{uploaded_file.name.rsplit(".", 1)[0]}.jpg')
