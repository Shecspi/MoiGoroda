from __future__ import annotations

from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from city.services.photo_processing import compress_city_photo


def _build_uploaded_image(size: tuple[int, int]) -> SimpleUploadedFile:
    buffer = BytesIO()
    image = Image.new('RGB', size, color=(100, 140, 190))
    image.save(buffer, format='PNG')
    return SimpleUploadedFile('sample.png', buffer.getvalue(), content_type='image/png')


@pytest.mark.unit
def test_compress_city_photo_converts_to_jpeg_and_resizes() -> None:
    source = _build_uploaded_image((4000, 2500))
    compressed = compress_city_photo(source)

    image = Image.open(compressed)
    assert image.format == 'JPEG'
    assert max(image.size) <= 1920
    assert compressed.name.endswith('.jpg')
