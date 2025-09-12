# tests/test_api_search_region.py
import sys
from types import SimpleNamespace
from unittest.mock import Mock, MagicMock
import pytest

from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import ValidationError

# Замените путь к модулю при необходимости
from region.api import search_region


def _module_for_view():
    return sys.modules[search_region.__module__]


def _make_qs_mock(regions):
    """
    Мок queryset-а, поддерживающий:
      - order_by(...) -> self
      - filter(...) -> self
      - итерацию (возвращает regions)
    """
    qs = MagicMock()
    qs.order_by.return_value = qs
    qs.filter.return_value = qs
    qs.__iter__.return_value = iter(regions)
    return qs


def test_returns_400_when_query_empty(monkeypatch):
    factory = APIRequestFactory()
    request = factory.get('/', data={'query': ''})

    serializer_instance = Mock()
    serializer_instance.validated_data = {'query': ''}
    serializer_instance.is_valid = Mock()

    serializer_class_mock = Mock(return_value=serializer_instance)

    module = _module_for_view()
    monkeypatch.setattr(module, 'RegionSearchParamsSerializer', serializer_class_mock)
    monkeypatch.setattr(module, 'Region', SimpleNamespace(objects=Mock()))

    response = search_region(request)

    assert response.status_code == 400
    assert response.data == {'detail': 'Параметр query является обязательным'}
    serializer_class_mock.assert_called_once_with(data=request.GET)
    serializer_instance.is_valid.assert_called_once_with(raise_exception=True)


def test_returns_200_and_regions_list_without_country_filter(monkeypatch):
    factory = APIRequestFactory()
    request = factory.get('/', data={'query': 'mos'})

    serializer_instance = Mock()
    serializer_instance.validated_data = {'query': 'mos'}
    serializer_instance.is_valid = Mock()
    serializer_class_mock = Mock(return_value=serializer_instance)

    module = _module_for_view()
    monkeypatch.setattr(module, 'RegionSearchParamsSerializer', serializer_class_mock)

    regions = [SimpleNamespace(id=1, title='Moscow'), SimpleNamespace(id=2, title='Mosul')]
    qs = _make_qs_mock(regions)
    manager = Mock()
    manager.filter = Mock(return_value=qs)

    monkeypatch.setattr(module, 'Region', SimpleNamespace(objects=manager))

    response = search_region(request)

    assert response.status_code == 200
    assert response.data == [{'id': 1, 'title': 'Moscow'}, {'id': 2, 'title': 'Mosul'}]

    manager.filter.assert_called_once_with(title__icontains='mos')
    qs.order_by.assert_called_once_with('title')
    qs.filter.assert_not_called()


def test_returns_200_and_regions_list_with_country_filter(monkeypatch):
    factory = APIRequestFactory()
    request = factory.get('/', data={'query': 'mos', 'country_id': '5'})

    serializer_instance = Mock()
    serializer_instance.validated_data = {'query': 'mos', 'country_id': 5}
    serializer_instance.is_valid = Mock()
    serializer_class_mock = Mock(return_value=serializer_instance)

    module = _module_for_view()
    monkeypatch.setattr(module, 'RegionSearchParamsSerializer', serializer_class_mock)

    regions = [SimpleNamespace(id=10, full_name='Moscow')]
    qs = _make_qs_mock(regions)
    manager = Mock()
    manager.filter = Mock(return_value=qs)

    monkeypatch.setattr(module, 'Region', SimpleNamespace(objects=manager))

    response = search_region(request)

    assert response.status_code == 200
    assert response.data == [{'id': 10, 'full_name': 'Moscow'}]

    manager.filter.assert_called_once_with(title__icontains='mos')
    qs.order_by.assert_called_once_with('full_name')
    qs.filter.assert_called_once_with(country_id=5)


def test_serializer_is_valid_returns_400_response(monkeypatch):
    factory = APIRequestFactory()
    request = factory.get('/', data={'query': 'mos'})

    def fake_is_valid(*args, **kwargs):
        raise ValidationError({'query': ['invalid']})

    serializer_instance = Mock()
    serializer_instance.is_valid.side_effect = fake_is_valid
    serializer_instance.validated_data = {}

    serializer_class_mock = Mock(return_value=serializer_instance)
    module = _module_for_view()
    monkeypatch.setattr(module, 'RegionSearchParamsSerializer', serializer_class_mock)
    monkeypatch.setattr(module, 'Region', SimpleNamespace(objects=Mock()))

    response = search_region(request)

    assert response.status_code == 400
    assert response.data == {'query': ['invalid']}

