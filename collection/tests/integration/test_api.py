"""
Интеграционные тесты для API приложения collection.
"""

import pytest
from django.test import Client
from rest_framework import status

from collection.models import Collection


@pytest.mark.django_db
@pytest.mark.integration
class TestCollectionSearchAPI:
    """Тесты для API collection_search."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    @pytest.fixture
    def collections(self) -> list[Collection]:
        """Создает тестовые коллекции."""
        return [
            Collection.objects.create(title='Золотое кольцо'),
            Collection.objects.create(title='Серебряное кольцо'),
            Collection.objects.create(title='Столицы регионов'),
            Collection.objects.create(title='Города-миллионники'),
        ]

    def test_search_returns_matching_collections(
        self, client: Client, collections: list[Collection]
    ) -> None:
        """Проверяет что поиск возвращает соответствующие коллекции."""
        response = client.get('/api/collection/search', {'query': 'кольцо'})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert any(c['title'] == 'Золотое кольцо' for c in data)
        assert any(c['title'] == 'Серебряное кольцо' for c in data)

    def test_search_is_case_insensitive(
        self, client: Client, collections: list[Collection]
    ) -> None:
        """Проверяет что поиск нечувствителен к регистру."""
        response = client.get('/api/collection/search', {'query': 'ЗОЛОТОЕ'})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]['title'] == 'Золотое кольцо'

    def test_search_without_query_param_returns_400(self, client: Client) -> None:
        """Проверяет что отсутствие параметра query возвращает 400."""
        response = client.get('/api/collection/search')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_search_with_empty_query_returns_400(self, client: Client) -> None:
        """Проверяет что пустой query возвращает 400."""
        response = client.get('/api/collection/search', {'query': ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert 'query' in data

    def test_search_returns_empty_list_when_no_matches(
        self, client: Client, collections: list[Collection]
    ) -> None:
        """Проверяет что поиск возвращает пустой список при отсутствии совпадений."""
        response = client.get('/api/collection/search', {'query': 'несуществующее'})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 0

    def test_search_returns_all_fields(self, client: Client, collections: list[Collection]) -> None:
        """Проверяет что ответ содержит все необходимые поля."""
        response = client.get('/api/collection/search', {'query': 'Золотое'})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        collection = data[0]
        assert 'id' in collection
        assert 'title' in collection
        assert collection['title'] == 'Золотое кольцо'

    def test_search_orders_results_by_title(
        self, client: Client, collections: list[Collection]
    ) -> None:
        """Проверяет что результаты отсортированы по названию."""
        response = client.get('/api/collection/search', {'query': 'кольцо'})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        titles = [c['title'] for c in data]
        assert titles == sorted(titles)

    def test_search_partial_match(self, client: Client, collections: list[Collection]) -> None:
        """Проверяет что поиск работает с частичным совпадением."""
        response = client.get('/api/collection/search', {'query': 'рег'})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]['title'] == 'Столицы регионов'

    def test_search_with_special_characters(self, client: Client) -> None:
        """Проверяет поиск со спецсимволами."""
        Collection.objects.create(title='Города-герои')

        response = client.get('/api/collection/search', {'query': 'Города-герои'})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1

    def test_search_endpoint_url(self, client: Client) -> None:
        """Проверяет что эндпоинт доступен по правильному URL."""
        response = client.get('/api/collection/search', {'query': 'test'})

        # Должен вернуть 200 даже если ничего не найдено
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
