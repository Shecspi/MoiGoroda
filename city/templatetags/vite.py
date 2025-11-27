"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import json
from pathlib import Path
from typing import Any, cast

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe, SafeString

register = template.Library()

_manifest: dict[str, Any] | None = None
_manifest_mtime: float | None = None


def get_manifest() -> dict[str, Any]:
    """
    Загружает manifest.json из Vite сборки.

    В development режиме ищет файл в BASE_DIR/static/js/manifest.json.
    В production режиме сначала проверяет STATIC_ROOT/js/manifest.json,
    затем BASE_DIR/static/js/manifest.json (на случай, если STATIC_ROOT не установлен).
    """
    global _manifest, _manifest_mtime

    # Определяем возможные пути к manifest.json
    possible_paths = []

    if settings.DEBUG:
        # В development режиме используем только путь в исходной директории
        possible_paths.append(Path(settings.BASE_DIR) / 'static/js/manifest.json')
    else:
        # В production режиме сначала проверяем STATIC_ROOT (если установлен)
        if settings.STATIC_ROOT:
            possible_paths.append(Path(settings.STATIC_ROOT) / 'js/manifest.json')
        # Затем проверяем исходную директорию (на случай, если STATIC_ROOT не установлен)
        possible_paths.append(Path(settings.BASE_DIR) / 'static/js/manifest.json')

    # Ищем первый существующий файл
    manifest_path = None
    for path in possible_paths:
        if path.exists():
            manifest_path = path
            break

    if manifest_path is None:
        if settings.DEBUG:
            return {}
        _manifest = {}
        _manifest_mtime = None
        return _manifest

    if settings.DEBUG:
        try:
            with open(manifest_path, 'r') as f:
                return cast(dict[str, Any], json.load(f))
        except FileNotFoundError:
            return {}

    try:
        current_mtime = manifest_path.stat().st_mtime
    except FileNotFoundError:
        _manifest = {}
        _manifest_mtime = None
        return _manifest

    if _manifest is None or _manifest_mtime != current_mtime:
        with open(manifest_path, 'r') as f:
            _manifest = cast(dict[str, Any], json.load(f))
        _manifest_mtime = current_mtime

    return _manifest


@register.simple_tag
def vite_asset(name: str) -> SafeString:
    # Django test runner принудительно устанавливает DEBUG=False, проверяем TESTING
    if settings.DEBUG or settings.TESTING:
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
    is_testing = getattr(settings, 'TESTING', False)

    if settings.DEBUG or is_testing:
        return mark_safe(f'<link rel="stylesheet" href="http://localhost:5173/{name}.css">')

    manifest = get_manifest()
    entry = manifest.get(f'{name}.css')

    if not entry:
        raise ValueError(f"CSS asset '{name}.css' not found in manifest.json")

    # Vite создаёт для CSS entry объект с полем 'file', содержащим путь к минифицированному CSS
    css_file = entry.get('file')
    if not css_file:
        raise ValueError(f"CSS file not found for '{name}' in manifest.json")

    return mark_safe(f'<link rel="stylesheet" href="{settings.STATIC_URL}js/{css_file}">')
