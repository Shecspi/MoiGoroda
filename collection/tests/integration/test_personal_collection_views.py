"""
Интеграционные тесты для views персональных коллекций.
"""

from typing import Any

import pytest
from django.test import Client

from city.models import City
from collection.models import PersonalCollection
from country.models import Country, Location, PartOfTheWorld
from region.models import Area, Region, RegionType


@pytest.fixture
def setup_view_data(django_user_model: Any) -> dict[str, Any]:
    """Создает тестовые данные для тестов views."""
    # Создаем пользователей
    user1 = django_user_model.objects.create_user(username='user1', password='testpass123')
    user2 = django_user_model.objects.create_user(username='user2', password='testpass123')

    # Создаем страну, регион и города

    part_of_world = PartOfTheWorld.objects.create(name='Европа')
    location = Location.objects.create(name='Восточная Европа', part_of_the_world=part_of_world)
    country = Country.objects.create(
        name='Россия', code='RU', fullname='Российская Федерация', location=location
    )
    region_type = RegionType.objects.create(title='Область')
    area = Area.objects.create(country=country, title='Центральный')
    region = Region.objects.create(
        title='Московская',
        country=country,
        type=region_type,
        area=area,
        iso3166='RU-MOS',
        full_name='Московская область',
    )

    cities = [
        City.objects.create(
            title='Москва',
            country=country,
            region=region,
            coordinate_width=55.75,
            coordinate_longitude=37.62,
        ),
        City.objects.create(
            title='Санкт-Петербург',
            country=country,
            region=region,
            coordinate_width=59.93,
            coordinate_longitude=30.34,
        ),
    ]

    # Создаем коллекции
    public_collection = PersonalCollection.objects.create(
        user=user1, title='Публичная коллекция', is_public=True
    )
    public_collection.city.set(cities)

    private_collection = PersonalCollection.objects.create(
        user=user1, title='Приватная коллекция', is_public=False
    )
    private_collection.city.set([cities[0]])

    return {
        'user1': user1,
        'user2': user2,
        'cities': cities,
        'public_collection': public_collection,
        'private_collection': private_collection,
    }


@pytest.mark.django_db
@pytest.mark.integration
class TestPersonalCollectionListView:
    """Тесты для PersonalCollectionListView."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    def test_list_view_requires_authentication(
        self, client: Client, setup_view_data: dict[str, Any]
    ) -> None:
        """Проверяет что список коллекций требует авторизации."""
        response = client.get('/collection/personal')
        # Должен быть редирект на страницу входа
        assert response.status_code in [302, 401]

    def test_list_view_shows_user_collections(
        self, client: Client, setup_view_data: dict[str, Any]
    ) -> None:
        """Проверяет что список показывает коллекции пользователя."""
        user1 = setup_view_data['user1']
        client.force_login(user1)

        response = client.get('/collection/personal')

        assert response.status_code == 200
        assert 'object_list' in response.context
        collections = list(response.context['object_list'])
        assert len(collections) == 2  # public и private коллекции

    def test_list_view_context_data(self, client: Client, setup_view_data: dict[str, Any]) -> None:
        """Проверяет контекст данных списка коллекций."""
        user1 = setup_view_data['user1']
        client.force_login(user1)

        response = client.get('/collection/personal')

        assert response.status_code == 200
        context = response.context
        assert 'active_page' in context
        assert context['active_page'] == 'collection'
        assert 'page_title' in context


@pytest.mark.django_db
@pytest.mark.integration
class TestPublicPersonalCollectionListView:
    """Тесты для PublicPersonalCollectionListView."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    def test_public_list_view_shows_only_public_collections(
        self, client: Client, setup_view_data: dict[str, Any]
    ) -> None:
        """Проверяет что список показывает только публичные коллекции."""
        response = client.get('/collection/personal/public')

        assert response.status_code == 200
        assert 'object_list' in response.context
        collections = list(response.context['object_list'])
        # Должна быть только публичная коллекция
        assert len(collections) == 1
        assert collections[0].is_public is True

    def test_public_list_view_accessible_without_auth(
        self, client: Client, setup_view_data: dict[str, Any]
    ) -> None:
        """Проверяет что публичный список доступен без авторизации."""
        response = client.get('/collection/personal/public')
        assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.integration
class TestPersonalCollectionCityListView:
    """Тесты для PersonalCollectionCityListView."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    def test_city_list_view_owner_access(
        self, client: Client, setup_view_data: dict[str, Any]
    ) -> None:
        """Проверяет доступ владельца к списку городов коллекции."""
        user1 = setup_view_data['user1']
        collection = setup_view_data['public_collection']
        client.force_login(user1)

        response = client.get(f'/collection/personal/{collection.id}/list')

        assert response.status_code == 200
        assert 'object_list' in response.context
        assert 'collection' in response.context

    def test_city_list_view_public_collection_access(
        self, client: Client, setup_view_data: dict[str, Any]
    ) -> None:
        """Проверяет доступ к публичной коллекции без авторизации."""
        collection = setup_view_data['public_collection']

        response = client.get(f'/collection/personal/{collection.id}/list')

        assert response.status_code == 200

    def test_city_list_view_private_collection_no_access(
        self, client: Client, setup_view_data: dict[str, Any]
    ) -> None:
        """Проверяет что приватная коллекция недоступна без авторизации."""
        collection = setup_view_data['private_collection']

        response = client.get(f'/collection/personal/{collection.id}/list')

        assert response.status_code == 404

    def test_city_list_view_private_collection_other_user_no_access(
        self, client: Client, setup_view_data: dict[str, Any]
    ) -> None:
        """Проверяет что другой пользователь не может видеть приватную коллекцию."""
        user2 = setup_view_data['user2']
        collection = setup_view_data['private_collection']
        client.force_login(user2)

        response = client.get(f'/collection/personal/{collection.id}/list')

        assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.integration
class TestPersonalCollectionCreateView:
    """Тесты для PersonalCollectionCreateView."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    def test_create_view_requires_authentication(self, client: Client) -> None:
        """Проверяет что страница создания требует авторизации."""
        response = client.get('/collection/personal/create')
        # Должен быть редирект на страницу входа
        assert response.status_code in [302, 401]

    def test_create_view_accessible_for_authenticated_user(
        self, client: Client, setup_view_data: dict[str, Any]
    ) -> None:
        """Проверяет что страница создания доступна авторизованному пользователю."""
        user1 = setup_view_data['user1']
        client.force_login(user1)

        response = client.get('/collection/personal/create')

        assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.integration
class TestPersonalCollectionEditView:
    """Тесты для PersonalCollectionEditView."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    def test_edit_view_requires_authentication(
        self, client: Client, setup_view_data: dict[str, Any]
    ) -> None:
        """Проверяет что страница редактирования требует авторизации."""
        collection = setup_view_data['public_collection']
        response = client.get(f'/collection/personal/{collection.id}/edit')
        # Должен быть редирект на страницу входа
        assert response.status_code in [302, 401]

    def test_edit_view_owner_access(self, client: Client, setup_view_data: dict[str, Any]) -> None:
        """Проверяет доступ владельца к странице редактирования."""
        user1 = setup_view_data['user1']
        collection = setup_view_data['public_collection']
        client.force_login(user1)

        response = client.get(f'/collection/personal/{collection.id}/edit')

        assert response.status_code == 200
        assert 'collection' in response.context
        assert response.context['collection'] == collection

    def test_edit_view_other_user_no_access(
        self, client: Client, setup_view_data: dict[str, Any]
    ) -> None:
        """Проверяет что другой пользователь не может редактировать коллекцию."""
        user2 = setup_view_data['user2']
        collection = setup_view_data['public_collection']
        client.force_login(user2)

        response = client.get(f'/collection/personal/{collection.id}/edit')

        assert response.status_code == 404
