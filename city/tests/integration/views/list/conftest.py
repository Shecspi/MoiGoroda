"""
Общие фикстуры для тестов списка посещённых городов.

Многие тесты подменяют ``get_unique_visited_cities`` списком моков вместо QuerySet.
Во view после этого вызывается ``annotate_visited_city_list_default_photo`` (SQL annotate),
что для списка недопустимо — подменяем функцию на тождественную.
"""

from __future__ import annotations

from typing import Any

import pytest


@pytest.fixture(autouse=True)
def passthrough_visited_city_list_default_photo_annotation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _passthrough(queryset: Any, user_id: int) -> Any:
        return queryset

    monkeypatch.setattr(
        'city.views.annotate_visited_city_list_default_photo',
        _passthrough,
        raising=True,
    )


@pytest.fixture(autouse=True)
def noop_attach_default_city_user_photo_urls(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Моки VisitedCity не задают UUID для default_city_user_photo_id; у MagicMock
    «левое» значение ломает attach_default_city_user_photo_presigned_urls.
    """

    def _noop(_items: Any, _user_id: int) -> None:
        return None

    monkeypatch.setattr(
        'city.views.attach_default_city_user_photo_presigned_urls',
        _noop,
        raising=True,
    )
