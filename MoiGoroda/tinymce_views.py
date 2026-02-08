"""
Обработчик загрузки изображений для TinyMCE.
Сохраняет в S3 через django-storages.
"""

import uuid

from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@staff_member_required
@require_http_methods(['POST'])
def upload_image(request):
    """Принимает изображение от TinyMCE, сохраняет в S3, возвращает URL."""
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'Нет файла'}, status=400)

    file = request.FILES['file']
    allowed_types = ('image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp')
    if file.content_type not in allowed_types:
        return JsonResponse({'error': f'Недопустимый тип: {file.content_type}'}, status=400)

    ext = file.name.split('.')[-1] if '.' in file.name else 'jpg'
    name = f'moi-goroda-blog/{uuid.uuid4().hex}.{ext}'
    path = default_storage.save(name, file)
    url = default_storage.url(path)
    return JsonResponse({'location': request.build_absolute_uri(url)})
