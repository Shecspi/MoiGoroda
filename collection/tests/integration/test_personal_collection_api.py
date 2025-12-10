"""
Интеграционные тесты для API персональных коллекций.
"""

import uuid
from typing import Any

import pytest
from django.test import Client
from rest_framework import status

from city.models import City
from collection.models import PersonalCollection
from country.models import Country, Location, PartOfTheWorld
from region.models import Area, Region, RegionType


@pytest.fixture
def setup_test_data(django_user_model: Any) -> dict[str, Any]:
    """Создает тестовые данные для API тестов."""
    # Создаем пользователей
    user1 = django_user_model.objects.create_user(
        username='user1', password='testpass123', email='user1@example.com'
    )
    user2 = django_user_model.objects.create_user(
        username='user2', password='testpass123', email='user2@example.com'
    )

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
        City.objects.create(
            title='Казань',
            country=country,
            region=region,
            coordinate_width=55.79,
            coordinate_longitude=49.12,
        ),
    ]

    return {
        'user1': user1,
        'user2': user2,
        'country': country,
        'region': region,
        'cities': cities,
    }


@pytest.mark.django_db
@pytest.mark.integration
class TestPersonalCollectionCreateAPI:
    """Тесты для API создания персональных коллекций."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    def test_create_collection_success(
        self, client: Client, setup_test_data: dict[str, Any]
    ) -> None:
        """Проверяет успешное создание коллекции."""
        user = setup_test_data['user1']
        cities = setup_test_data['cities']
        client.force_login(user)

        data = {
            'title': 'Моя коллекция',
            'city_ids': [cities[0].id, cities[1].id],
            'is_public': False,
        }

        response = client.post(
            '/api/collection/personal/create',
            data=data,
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert 'id' in response_data
        assert response_data['title'] == 'Моя коллекция'
        assert response_data['is_public'] is False

        # Проверяем что коллекция создана в БД
        collection = PersonalCollection.objects.get(id=response_data['id'])
        assert collection.user == user
        assert collection.title == 'Моя коллекция'
        assert collection.is_public is False
        assert collection.city.count() == 2
        assert cities[0] in collection.city.all()
        assert cities[1] in collection.city.all()

    def test_create_collection_without_auth(
        self, client: Client, setup_test_data: dict[str, Any]
    ) -> None:
        """Проверяет что неавторизованный пользователь не может создать коллекцию."""
        cities = setup_test_data['cities']
        data = {
            'title': 'Моя коллекция',
            'city_ids': [cities[0].id],
        }

        response = client.post(
            '/api/collection/personal/create',
            data=data,
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_collection_without_title(
        self, client: Client, setup_test_data: dict[str, Any]
    ) -> None:
        """Проверяет валидацию при отсутствии title."""
        user = setup_test_data['user1']
        cities = setup_test_data['cities']
        client.force_login(user)

        data = {'city_ids': [cities[0].id]}

        response = client.post(
            '/api/collection/personal/create',
            data=data,
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_collection_without_city_ids(
        self, client: Client, setup_test_data: dict[str, Any]
    ) -> None:
        """Проверяет валидацию при отсутствии city_ids."""
        user = setup_test_data['user1']
        client.force_login(user)

        data = {'title': 'Коллекция'}

        response = client.post(
            '/api/collection/personal/create',
            data=data,
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_collection_with_empty_city_ids(
        self, client: Client, setup_test_data: dict[str, Any]
    ) -> None:
        """Проверяет валидацию при пустом city_ids."""
        user = setup_test_data['user1']
        client.force_login(user)

        data = {'title': 'Коллекция', 'city_ids': []}

        response = client.post(
            '/api/collection/personal/create',
            data=data,
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_collection_with_nonexistent_city_ids(
        self, client: Client, setup_test_data: dict[str, Any]
    ) -> None:
        """Проверяет валидацию при несуществующих city_ids."""
        user = setup_test_data['user1']
        client.force_login(user)

        data = {'title': 'Коллекция', 'city_ids': [99999, 99998]}

        response = client.post(
            '/api/collection/personal/create',
            data=data,
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert 'missing_city_ids' in response_data

    def test_create_collection_with_public_true(
        self, client: Client, setup_test_data: dict[str, Any]
    ) -> None:
        """Проверяет создание публичной коллекции."""
        user = setup_test_data['user1']
        cities = setup_test_data['cities']
        client.force_login(user)

        data = {
            'title': 'Публичная коллекция',
            'city_ids': [cities[0].id],
            'is_public': True,
        }

        response = client.post(
            '/api/collection/personal/create',
            data=data,
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data['is_public'] is True

        collection = PersonalCollection.objects.get(id=response_data['id'])
        assert collection.is_public is True


@pytest.mark.django_db
@pytest.mark.integration
class TestPersonalCollectionUpdateAPI:
    """Тесты для API обновления персональных коллекций."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    @pytest.fixture
    def collection(self, setup_test_data: dict[str, Any]) -> PersonalCollection:
        """Создает тестовую коллекцию."""
        user = setup_test_data['user1']
        cities = setup_test_data['cities']
        collection = PersonalCollection.objects.create(
            user=user, title='Исходная коллекция', is_public=False
        )
        collection.city.set([cities[0], cities[1]])
        return collection

    def test_update_collection_success(
        self,
        client: Client,
        setup_test_data: dict[str, Any],
        collection: PersonalCollection,
    ) -> None:
        """Проверяет успешное обновление коллекции."""
        user = setup_test_data['user1']
        cities = setup_test_data['cities']
        client.force_login(user)

        data = {
            'title': 'Обновленная коллекция',
            'city_ids': [cities[1].id, cities[2].id],
            'is_public': True,
        }

        response = client.put(
            f'/api/collection/personal/{collection.id}/update',
            data=data,
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data['title'] == 'Обновленная коллекция'
        assert response_data['is_public'] is True

        # Проверяем что коллекция обновлена в БД
        collection.refresh_from_db()
        assert collection.title == 'Обновленная коллекция'
        assert collection.is_public is True
        assert collection.city.count() == 2
        assert cities[1] in collection.city.all()
        assert cities[2] in collection.city.all()

    def test_update_collection_by_other_user(
        self,
        client: Client,
        setup_test_data: dict[str, Any],
        collection: PersonalCollection,
    ) -> None:
        """Проверяет что другой пользователь не может обновить коллекцию."""
        user2 = setup_test_data['user2']
        cities = setup_test_data['cities']
        client.force_login(user2)

        data = {
            'title': 'Взломанная коллекция',
            'city_ids': [cities[0].id],
        }

        response = client.put(
            f'/api/collection/personal/{collection.id}/update',
            data=data,
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_nonexistent_collection(
        self, client: Client, setup_test_data: dict[str, Any]
    ) -> None:
        """Проверяет обновление несуществующей коллекции."""
        user = setup_test_data['user1']
        cities = setup_test_data['cities']
        client.force_login(user)

        fake_id = uuid.uuid4()
        data = {
            'title': 'Коллекция',
            'city_ids': [cities[0].id],
        }

        response = client.put(
            f'/api/collection/personal/{fake_id}/update',
            data=data,
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_collection_with_invalid_uuid(
        self, client: Client, setup_test_data: dict[str, Any]
    ) -> None:
        """Проверяет обновление с неверным форматом UUID."""
        user = setup_test_data['user1']
        client.force_login(user)

        data = {
            'title': 'Коллекция',
            'city_ids': [1],
        }

        response = client.put(
            '/api/collection/personal/invalid-uuid/update',
            data=data,
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.integration
class TestPersonalCollectionDeleteAPI:
    """Тесты для API удаления персональных коллекций."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    @pytest.fixture
    def collection(self, setup_test_data: dict[str, Any]) -> PersonalCollection:
        """Создает тестовую коллекцию."""
        user = setup_test_data['user1']
        cities = setup_test_data['cities']
        collection = PersonalCollection.objects.create(
            user=user, title='Коллекция для удаления', is_public=False
        )
        collection.city.set([cities[0]])
        return collection

    def test_delete_collection_success(
        self,
        client: Client,
        setup_test_data: dict[str, Any],
        collection: PersonalCollection,
    ) -> None:
        """Проверяет успешное удаление коллекции."""
        user = setup_test_data['user1']
        client.force_login(user)

        collection_id = collection.id

        response = client.delete(f'/api/collection/personal/{collection_id}/delete')

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Проверяем что коллекция удалена из БД
        assert not PersonalCollection.objects.filter(id=collection_id).exists()

    def test_delete_collection_by_other_user(
        self,
        client: Client,
        setup_test_data: dict[str, Any],
        collection: PersonalCollection,
    ) -> None:
        """Проверяет что другой пользователь не может удалить коллекцию."""
        user2 = setup_test_data['user2']
        client.force_login(user2)

        response = client.delete(f'/api/collection/personal/{collection.id}/delete')

        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Проверяем что коллекция не удалена
        assert PersonalCollection.objects.filter(id=collection.id).exists()

    def test_delete_nonexistent_collection(
        self, client: Client, setup_test_data: dict[str, Any]
    ) -> None:
        """Проверяет удаление несуществующей коллекции."""
        user = setup_test_data['user1']
        client.force_login(user)

        fake_id = uuid.uuid4()
        response = client.delete(f'/api/collection/personal/{fake_id}/delete')

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.integration
class TestPersonalCollectionCopyAPI:
    """Тесты для API копирования персональных коллекций."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    @pytest.fixture
    def public_collection(self, setup_test_data: dict[str, Any]) -> PersonalCollection:
        """Создает публичную коллекцию для копирования."""
        user1 = setup_test_data['user1']
        cities = setup_test_data['cities']
        collection = PersonalCollection.objects.create(
            user=user1, title='Публичная коллекция', is_public=True
        )
        collection.city.set(cities)
        return collection

    def test_copy_public_collection_success(
        self,
        client: Client,
        setup_test_data: dict[str, Any],
        public_collection: PersonalCollection,
    ) -> None:
        """Проверяет успешное копирование публичной коллекции."""
        user2 = setup_test_data['user2']
        client.force_login(user2)

        response = client.post(
            f'/api/collection/personal/{public_collection.id}/copy',
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert 'id' in response_data
        assert response_data['title'] == 'Публичная коллекция'
        assert response_data['is_public'] is False  # Копия приватная

        # Проверяем что коллекция скопирована
        copied_collection = PersonalCollection.objects.get(id=response_data['id'])
        assert copied_collection.user == user2
        assert copied_collection.title == public_collection.title
        assert copied_collection.is_public is False
        assert copied_collection.city.count() == public_collection.city.count()

    def test_copy_own_collection(
        self,
        client: Client,
        setup_test_data: dict[str, Any],
        public_collection: PersonalCollection,
    ) -> None:
        """Проверяет что нельзя скопировать свою коллекцию."""
        user1 = setup_test_data['user1']
        client.force_login(user1)

        response = client.post(
            f'/api/collection/personal/{public_collection.id}/copy',
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        response_data = response.json()
        assert 'Нельзя скопировать свою коллекцию' in response_data['detail']

    def test_copy_private_collection(self, client: Client, setup_test_data: dict[str, Any]) -> None:
        """Проверяет что нельзя скопировать приватную коллекцию."""
        user1 = setup_test_data['user1']
        user2 = setup_test_data['user2']
        cities = setup_test_data['cities']
        client.force_login(user2)

        private_collection = PersonalCollection.objects.create(
            user=user1, title='Приватная коллекция', is_public=False
        )
        private_collection.city.set([cities[0]])

        response = client.post(
            f'/api/collection/personal/{private_collection.id}/copy',
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        response_data = response.json()
        assert 'Нельзя скопировать приватную коллекцию' in response_data['detail']

    def test_copy_nonexistent_collection(
        self, client: Client, setup_test_data: dict[str, Any]
    ) -> None:
        """Проверяет копирование несуществующей коллекции."""
        user2 = setup_test_data['user2']
        client.force_login(user2)

        fake_id = uuid.uuid4()
        response = client.post(
            f'/api/collection/personal/{fake_id}/copy',
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.integration
class TestPersonalCollectionUpdatePublicStatusAPI:
    """Тесты для API изменения статуса публичности."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    @pytest.fixture
    def collection(self, setup_test_data: dict[str, Any]) -> PersonalCollection:
        """Создает тестовую коллекцию."""
        user = setup_test_data['user1']
        cities = setup_test_data['cities']
        collection = PersonalCollection.objects.create(
            user=user, title='Коллекция', is_public=False
        )
        collection.city.set([cities[0]])
        return collection

    def test_update_public_status_to_true(
        self,
        client: Client,
        setup_test_data: dict[str, Any],
        collection: PersonalCollection,
    ) -> None:
        """Проверяет изменение статуса на публичный."""
        user = setup_test_data['user1']
        client.force_login(user)

        data = {'is_public': True}

        response = client.patch(
            f'/api/collection/personal/{collection.id}/update-public-status',
            data=data,
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data['is_public'] is True

        collection.refresh_from_db()
        assert collection.is_public is True

    def test_update_public_status_to_false(
        self,
        client: Client,
        setup_test_data: dict[str, Any],
        collection: PersonalCollection,
    ) -> None:
        """Проверяет изменение статуса на приватный."""
        user = setup_test_data['user1']
        collection.is_public = True
        collection.save()
        client.force_login(user)

        data = {'is_public': False}

        response = client.patch(
            f'/api/collection/personal/{collection.id}/update-public-status',
            data=data,
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data['is_public'] is False

        collection.refresh_from_db()
        assert collection.is_public is False

    def test_update_public_status_by_other_user(
        self,
        client: Client,
        setup_test_data: dict[str, Any],
        collection: PersonalCollection,
    ) -> None:
        """Проверяет что другой пользователь не может изменить статус."""
        user2 = setup_test_data['user2']
        client.force_login(user2)

        data = {'is_public': True}

        response = client.patch(
            f'/api/collection/personal/{collection.id}/update-public-status',
            data=data,
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
