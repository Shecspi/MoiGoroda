"""
Обработчик загрузки изображений для TinyMCE.
Сохраняет в S3 через django-storages.
"""

import uuid
from typing import cast

from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods

_ALLOWED_IMAGE_TYPES = ('image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp')


@staff_member_required
@require_http_methods(['POST'])
def upload_image(request: HttpRequest) -> JsonResponse:
    """Принимает изображение от TinyMCE, сохраняет в S3, возвращает URL."""
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'Нет файла'}, status=400)

    raw = request.FILES['file']
    file = cast(UploadedFile, raw[0] if isinstance(raw, list) else raw)
    content_type = file.content_type or ''
    if content_type not in _ALLOWED_IMAGE_TYPES:
        return JsonResponse({'error': f'Недопустимый тип: {content_type}'}, status=400)

    file_name = file.name or 'image'
    ext = file_name.split('.')[-1] if '.' in file_name else 'jpg'
    name = f'blog/{uuid.uuid4().hex}.{ext}'
    path = default_storage.save(name, file)
    url = default_storage.url(path)
    return JsonResponse({'location': request.build_absolute_uri(url)})
