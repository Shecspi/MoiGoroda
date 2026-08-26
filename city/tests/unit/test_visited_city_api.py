# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

"""Unit-тесты сериализации ответа DMR API посещений."""

from datetime import date
from types import SimpleNamespace
from typing import cast

import pytest

from city.api.visited import _visit_payload
from city.models import VisitedCity


@pytest.mark.unit
def test_visit_payload_converts_markdown_safe_string_to_plain_string() -> None:
    """DMR JSON renderer не умеет сериализовать django SafeString."""
    visit = cast(
        VisitedCity,
        SimpleNamespace(
            id=1,
            city=SimpleNamespace(
                id=2,
                title='Тверь',
                region_id=3,
                region='Тверская область',
                country=SimpleNamespace(name='Россия'),
                coordinate_width=56.8587,
                coordinate_longitude=35.9176,
            ),
            date_of_visit=date(2026, 8, 8),
            has_magnet=False,
            impression='**Отличная поездка**',
            rating=5,
        ),
    )

    payload = _visit_payload(visit)

    assert type(payload['impression_html']) is str
    assert payload['impression_html'] == '<p><strong>Отличная поездка</strong></p>'
