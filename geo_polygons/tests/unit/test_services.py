from __future__ import annotations

from typing import Any

import pytest

from geo_polygons.domain.services import GetPolygonService
from geo_polygons.tests.conftest import RELATION_ID, make_polygon


@pytest.mark.unit
def test_get_polygon_service_returns_cached_polygon_without_external_call(mocker: Any) -> None:
    polygon = make_polygon()
    repository = mocker.Mock()
    repository.get_by_relation_id.return_value = polygon
    external = mocker.Mock()

    result = GetPolygonService(repository, external).execute(RELATION_ID)

    assert result == polygon
    repository.get_by_relation_id.assert_called_once_with(RELATION_ID)
    external.fetch_polygon.assert_not_called()
    repository.save.assert_not_called()


@pytest.mark.unit
def test_get_polygon_service_fetches_and_saves_when_cache_miss(mocker: Any) -> None:
    polygon = make_polygon()
    repository = mocker.Mock()
    repository.get_by_relation_id.return_value = None
    external = mocker.Mock()
    external.fetch_polygon.return_value = polygon

    result = GetPolygonService(repository, external).execute(RELATION_ID)

    assert result == polygon
    external.fetch_polygon.assert_called_once_with(RELATION_ID)
    repository.save.assert_called_once_with(polygon)


@pytest.mark.unit
def test_get_polygon_service_returns_none_when_not_found(mocker: Any) -> None:
    repository = mocker.Mock()
    repository.get_by_relation_id.return_value = None
    external = mocker.Mock()
    external.fetch_polygon.return_value = None

    result = GetPolygonService(repository, external).execute(RELATION_ID)

    assert result is None
    repository.save.assert_not_called()
