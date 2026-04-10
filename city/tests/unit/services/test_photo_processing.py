from __future__ import annotations

from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from PIL.Image import DecompressionBombError

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
    assert compressed.name is not None
    assert compressed.name.endswith('.jpg')


@pytest.mark.unit
def test_compress_city_photo_rejects_too_many_pixels(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('city.services.photo_processing.settings.CITY_USER_PHOTO_MAX_PIXELS', 5000)
    source = _build_uploaded_image((100, 100))

    with pytest.raises(ValueError, match='Слишком большое изображение'):
        compress_city_photo(source)


@pytest.mark.unit
def test_compress_city_photo_rejects_decompression_bomb(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _build_uploaded_image((200, 200))

    def _raise_decompression_bomb(_: object) -> None:
        raise DecompressionBombError('boom')

    monkeypatch.setattr('city.services.photo_processing.Image.open', _raise_decompression_bomb)

    with pytest.raises(ValueError, match='Неподдерживаемый формат изображения'):
        compress_city_photo(source)
