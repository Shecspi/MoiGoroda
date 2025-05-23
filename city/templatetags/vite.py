import json
from pathlib import Path
from django import template
from django.conf import settings

register = template.Library()

_manifest = None


def get_manifest():
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
def vite_asset(name):
    if settings.DEBUG:
        return f'http://localhost:5173/{name}'
    manifest = get_manifest()
    entry = manifest.get(name)
    if not entry:
        raise ValueError(f"Asset '{name}' not found in manifest.json")
    return f"{settings.STATIC_URL}js/{entry['file']}"
