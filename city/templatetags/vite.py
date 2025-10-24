"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import json
import os
from pathlib import Path
from typing import Any

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe, SafeString

register = template.Library()

_manifest: dict[str, Any] | None = None


def get_manifest() -> dict[str, Any]:
    global _manifest
    if _manifest is None:
        manifest_path = Path(settings.BASE_DIR) / 'static/js/manifest.json'
        try:
            with open(manifest_path, 'r') as f:
                _manifest = json.load(f)
        except FileNotFoundError:
            _manifest = {}
    return _manifest


@register.simple_tag
def vite_asset(name: str) -> SafeString:
    # Django test runner принудительно устанавливает DEBUG=False, проверяем TESTING
    is_testing = os.getenv('TESTING') == 'True'

    if settings.DEBUG or is_testing:
        return mark_safe(f'<script type="module" src="http://localhost:5173/{name}"></script>')

    manifest = get_manifest()
    entry = manifest.get(name)
    if not entry:
        raise ValueError(f"Asset '{name}' not found in manifest.json")

    tags = []

    # Подключаем CSS-файлы
    for css_file in entry.get('css', []):
        tags.append(f'<link rel="stylesheet" href="{settings.STATIC_URL}js/{css_file}">')

    # Подключаем JS-файл
    tags.append(f'<script type="module" src="{settings.STATIC_URL}js/{entry["file"]}"></script>')

    return mark_safe('\n'.join(tags))


@register.simple_tag
def vite_css(name: str) -> SafeString:
    """
    Подключает только CSS файл из Vite сборки без JS.
    Используется для страниц, где нужны только стили.

    Args:
        name: Имя CSS entry в vite.config.js (например, 'css/style')

    Returns:
        HTML тег <link> для подключения CSS
    """
    # Django test runner принудительно устанавливает DEBUG=False, проверяем TESTING
    is_testing = os.getenv('TESTING') == 'True'

    if settings.DEBUG or is_testing:
        # В dev режиме подключаем CSS из frontend/css/ через Django staticfiles
        # Django находит их через STATICFILES_DIRS
        # Используем полный путь для файлов в подпапках
        return mark_safe(f'<link rel="stylesheet" href="{settings.STATIC_URL}{name}.css">')

    manifest = get_manifest()
    entry = manifest.get(f'{name}.css')
    if not entry:
        raise ValueError(f"CSS asset '{name}.css' not found in manifest.json")

    # Vite создаёт для CSS entry объект с полем 'file', содержащим путь к минифицированному CSS
    css_file = entry.get('file')
    if not css_file:
        raise ValueError(f"CSS file not found for '{name}' in manifest.json")

    return mark_safe(f'<link rel="stylesheet" href="{settings.STATIC_URL}js/{css_file}">')
