# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

import pytest
from django.test import override_settings

from city.templatetags.vite import collect_entry_css_files, vite_asset, vite_css


@pytest.mark.unit
def test_collect_entry_css_files_includes_import_chunks() -> None:
    manifest = {
        'js/entries/content_image_gallery.js': {
            'file': 'assets/content_image_gallery-febf2a7f.js',
            'imports': ['_free-mode-b542fbb5.js', '__commonjsHelpers-725317a4.js'],
        },
        '_free-mode-b542fbb5.js': {
            'file': 'assets/free-mode-b542fbb5.js',
            'css': ['assets/free-mode-ae5d35e1.css'],
        },
        '__commonjsHelpers-725317a4.js': {
            'file': 'assets/_commonjsHelpers-725317a4.js',
        },
    }

    css_files = collect_entry_css_files(manifest, 'js/entries/content_image_gallery.js')

    assert css_files == ['assets/free-mode-ae5d35e1.css']


@pytest.mark.unit
def test_collect_entry_css_files_deduplicates_css() -> None:
    manifest = {
        'entry.js': {
            'css': ['assets/shared.css'],
            'imports': ['chunk-a.js', 'chunk-b.js'],
        },
        'chunk-a.js': {
            'css': ['assets/shared.css', 'assets/a.css'],
        },
        'chunk-b.js': {
            'css': ['assets/shared.css', 'assets/b.css'],
        },
    }

    css_files = collect_entry_css_files(manifest, 'entry.js')

    assert css_files == ['assets/shared.css', 'assets/a.css', 'assets/b.css']


@pytest.mark.unit
@override_settings(DEBUG=True, TESTING=False)
def test_vite_asset_uses_vite_base_path_in_development() -> None:
    html = str(vite_asset('js/entries/notification.js'))

    assert 'src="http://localhost:5173/static/js/js/entries/notification.js"' in html


@pytest.mark.unit
@override_settings(DEBUG=True, TESTING=False)
def test_vite_css_uses_vite_base_path_in_development() -> None:
    html = str(vite_css('css/tailwind'))

    assert 'href="http://localhost:5173/static/js/css/tailwind.css"' in html


@pytest.mark.unit
@override_settings(DEBUG=False, STATIC_URL='/static/', TESTING=False)
def test_vite_asset_includes_css_from_import_chunks() -> None:
    from city.templatetags import vite as vite_module

    manifest = {
        'js/entries/content_image_gallery.js': {
            'file': 'assets/content_image_gallery-febf2a7f.js',
            'imports': ['_free-mode-b542fbb5.js'],
        },
        '_free-mode-b542fbb5.js': {
            'file': 'assets/free-mode-b542fbb5.js',
            'css': ['assets/free-mode-ae5d35e1.css'],
        },
    }

    original_get_manifest = vite_module.get_manifest
    vite_module.get_manifest = lambda: manifest
    try:
        html = str(vite_asset('js/entries/content_image_gallery.js'))
    finally:
        vite_module.get_manifest = original_get_manifest

    assert 'href="/static/js/assets/free-mode-ae5d35e1.css"' in html
    assert 'src="/static/js/assets/content_image_gallery-febf2a7f.js"' in html
