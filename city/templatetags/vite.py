import json
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
    # Временная диагностика для отладки
    import os
    import sys
    print(f"🔍 vite_asset called for: {name}")
    print(f"  settings.DEBUG: {settings.DEBUG}")
    print(f"  os.getenv('DEBUG'): {os.getenv('DEBUG')}")
    print(f"  os.getenv('TESTING'): {os.getenv('TESTING')}")
    print(f"  'pytest' in sys.modules: {'pytest' in sys.modules}")
    
    if settings.DEBUG:
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
