"""
E2E тесты для полных сценариев работы с персональными коллекциями.
Полные пути пользователя: создание -> просмотр -> редактирование -> копирование -> удаление.
"""

import uuid
from typing import Any

import pytest
from django.test import Client

from city.models import City
from collection.models import PersonalCollection
from country.models import Country, Location, PartOfTheWorld
from region.models import Area, Region, RegionType


@pytest.fixture
def setup_e2e_data(django_user_model: Any) -> dict[str, Any]:
    """Создает тестовые данные для E2E тестов."""
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
        City.objects.create(
            title='Новосибирск',
            country=country,
            region=region,
            coordinate_width=55.01,
            coordinate_longitude=82.93,
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
@pytest.mark.e2e
class TestPersonalCollectionFullWorkflow:
    """E2E тесты для полного сценария работы с персональными коллекциями."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    def test_complete_collection_lifecycle(
        self, client: Client, setup_e2e_data: dict[str, Any]
    ) -> None:
        """
        Полный жизненный цикл коллекции:
        1. Создание коллекции через API
        2. Просмотр списка коллекций
        3. Просмотр городов коллекции
        4. Редактирование коллекции через API
        5. Изменение статуса публичности
        6. Удаление коллекции
        """
        user1 = setup_e2e_data['user1']
        cities = setup_e2e_data['cities']
        client.force_login(user1)

        # Шаг 1: Создание коллекции
        create_data = {
            'title': 'Моя первая коллекция',
            'city_ids': [cities[0].id, cities[1].id],
            'is_public': False,
        }
        response = client.post(
            '/api/collection/personal/create',
            data=create_data,
            content_type='application/json',
        )
        assert response.status_code == 201
        collection_data = response.json()
        collection_id = collection_data['id']

        # Проверяем что коллекция создана
        collection = PersonalCollection.objects.get(id=collection_id)
        assert collection.title == 'Моя первая коллекция'
        assert collection.is_public is False
        assert collection.city.count() == 2

        # Шаг 2: Просмотр списка коллекций
        response = client.get('/collection/personal')
        assert response.status_code == 200
        collections = list(response.context['object_list'])
        assert len(collections) == 1
        assert collections[0].id == uuid.UUID(collection_id)

        # Шаг 3: Просмотр городов коллекции
        response = client.get(f'/collection/personal/{collection_id}/list')
        assert response.status_code == 200
        assert 'collection' in response.context
        assert response.context['collection'].id == uuid.UUID(collection_id)

        # Шаг 4: Редактирование коллекции
        update_data = {
            'title': 'Обновленная коллекция',
            'city_ids': [cities[1].id, cities[2].id, cities[3].id],
            'is_public': True,
        }
        response = client.put(
            f'/api/collection/personal/{collection_id}/update',
            data=update_data,
            content_type='application/json',
        )
        assert response.status_code == 200
        collection.refresh_from_db()
        # Сохраняем значения в переменные для проверки
        title = collection.title
        is_public = collection.is_public
        city_count = collection.city.count()
        # Проверяем все значения
        assert title == 'Обновленная коллекция'
        assert is_public is True
        assert city_count == 3  # type: ignore[unreachable]

        # Шаг 5: Изменение статуса публичности
        status_data = {'is_public': False}
        response = client.patch(
            f'/api/collection/personal/{collection_id}/update-public-status',
            data=status_data,
            content_type='application/json',
        )
        assert response.status_code == 200
        collection.refresh_from_db()
        assert collection.is_public is False

        # Шаг 6: Удаление коллекции
        response = client.delete(f'/api/collection/personal/{collection_id}/delete')
        assert response.status_code == 204
        assert not PersonalCollection.objects.filter(id=collection_id).exists()

    def test_collection_copy_workflow(self, client: Client, setup_e2e_data: dict[str, Any]) -> None:
        """
        Полный сценарий копирования коллекции:
        1. User1 создает публичную коллекцию
        2. User2 копирует коллекцию
        3. User2 просматривает свою скопированную коллекцию
        4. User2 редактирует скопированную коллекцию
        """
        user1 = setup_e2e_data['user1']
        user2 = setup_e2e_data['user2']
        cities = setup_e2e_data['cities']

        # Шаг 1: User1 создает публичную коллекцию
        client.force_login(user1)
        create_data = {
            'title': 'Публичная коллекция для копирования',
            'city_ids': [cities[0].id, cities[1].id, cities[2].id],
            'is_public': True,
        }
        response = client.post(
            '/api/collection/personal/create',
            data=create_data,
            content_type='application/json',
        )
        assert response.status_code == 201
        original_collection_id = response.json()['id']

        # Шаг 2: User2 копирует коллекцию
        client.force_login(user2)
        response = client.post(
            f'/api/collection/personal/{original_collection_id}/copy',
            content_type='application/json',
        )
        assert response.status_code == 201
        copied_collection_data = response.json()
        copied_collection_id = copied_collection_data['id']

        # Проверяем что коллекция скопирована
        copied_collection = PersonalCollection.objects.get(id=copied_collection_id)
        assert copied_collection.user == user2
        assert copied_collection.title == 'Публичная коллекция для копирования'
        assert copied_collection.is_public is False  # Копия приватная
        assert copied_collection.is_copied is True  # Коллекция была скопирована
        assert copied_collection.city.count() == 3

        # Шаг 3: User2 просматривает свою скопированную коллекцию
        response = client.get(f'/collection/personal/{copied_collection_id}/list')
        assert response.status_code == 200
        assert response.context['collection'].id == uuid.UUID(copied_collection_id)

        # Шаг 4: User2 редактирует скопированную коллекцию
        update_data = {
            'title': 'Моя скопированная коллекция',
            'city_ids': [cities[2].id, cities[3].id],
            'is_public': False,
        }
        response = client.put(
            f'/api/collection/personal/{copied_collection_id}/update',
            data=update_data,
            content_type='application/json',
        )
        assert response.status_code == 200
        copied_collection.refresh_from_db()
        assert copied_collection.title == 'Моя скопированная коллекция'
        assert copied_collection.city.count() == 2

    def test_multiple_users_independent_collections(
        self, client: Client, setup_e2e_data: dict[str, Any]
    ) -> None:
        """
        Проверяет что коллекции разных пользователей независимы:
        1. User1 создает коллекцию
        2. User2 создает свою коллекцию
        3. Каждый видит только свои коллекции
        """
        user1 = setup_e2e_data['user1']
        user2 = setup_e2e_data['user2']
        cities = setup_e2e_data['cities']

        # User1 создает коллекцию
        client.force_login(user1)
        create_data1 = {
            'title': 'Коллекция User1',
            'city_ids': [cities[0].id],
            'is_public': False,
        }
        response = client.post(
            '/api/collection/personal/create',
            data=create_data1,
            content_type='application/json',
        )
        assert response.status_code == 201
        collection1_id = response.json()['id']

        # User2 создает коллекцию
        client.force_login(user2)
        create_data2 = {
            'title': 'Коллекция User2',
            'city_ids': [cities[1].id],
            'is_public': False,
        }
        response = client.post(
            '/api/collection/personal/create',
            data=create_data2,
            content_type='application/json',
        )
        assert response.status_code == 201
        collection2_id = response.json()['id']

        # User1 видит только свою коллекцию
        client.force_login(user1)
        response = client.get('/collection/personal')
        assert response.status_code == 200
        collections = list(response.context['object_list'])
        assert len(collections) == 1
        assert collections[0].id == uuid.UUID(collection1_id)

        # User2 видит только свою коллекцию
        client.force_login(user2)
        response = client.get('/collection/personal')
        assert response.status_code == 200
        collections = list(response.context['object_list'])
        assert len(collections) == 1
        assert collections[0].id == uuid.UUID(collection2_id)

    def test_public_collection_visibility(
        self, client: Client, setup_e2e_data: dict[str, Any]
    ) -> None:
        """
        Проверяет видимость публичных коллекций:
        1. User1 создает публичную коллекцию
        2. Неавторизованный пользователь видит её в списке публичных
        3. User2 видит её в списке публичных
        4. User2 может скопировать её
        """
        user1 = setup_e2e_data['user1']
        user2 = setup_e2e_data['user2']
        cities = setup_e2e_data['cities']

        # User1 создает публичную коллекцию
        client.force_login(user1)
        create_data = {
            'title': 'Публичная коллекция',
            'city_ids': [cities[0].id, cities[1].id],
            'is_public': True,
        }
        response = client.post(
            '/api/collection/personal/create',
            data=create_data,
            content_type='application/json',
        )
        assert response.status_code == 201
        collection_id = response.json()['id']

        # Неавторизованный пользователь видит коллекцию в списке публичных
        client.logout()
        response = client.get('/collection/personal/public')
        assert response.status_code == 200
        collections = list(response.context['object_list'])
        assert len(collections) == 1
        assert collections[0].id == uuid.UUID(collection_id)

        # Неавторизованный пользователь может просмотреть коллекцию
        response = client.get(f'/collection/personal/{collection_id}/list')
        assert response.status_code == 200

        # User2 видит коллекцию в списке публичных
        client.force_login(user2)
        response = client.get('/collection/personal/public')
        assert response.status_code == 200
        collections = list(response.context['object_list'])
        assert len(collections) == 1

        # User2 может скопировать коллекцию
        response = client.post(
            f'/api/collection/personal/{collection_id}/copy',
            content_type='application/json',
        )
        assert response.status_code == 201

    def test_private_collection_not_visible_to_others(
        self, client: Client, setup_e2e_data: dict[str, Any]
    ) -> None:
        """
        Проверяет что приватные коллекции не видны другим:
        1. User1 создает приватную коллекцию
        2. Неавторизованный пользователь не видит её
        3. User2 не видит её в списке публичных
        4. User2 не может получить доступ к коллекции
        """
        user1 = setup_e2e_data['user1']
        user2 = setup_e2e_data['user2']
        cities = setup_e2e_data['cities']

        # User1 создает приватную коллекцию
        client.force_login(user1)
        create_data = {
            'title': 'Приватная коллекция',
            'city_ids': [cities[0].id],
            'is_public': False,
        }
        response = client.post(
            '/api/collection/personal/create',
            data=create_data,
            content_type='application/json',
        )
        assert response.status_code == 201
        collection_id = response.json()['id']

        # Неавторизованный пользователь не видит коллекцию в списке публичных
        client.logout()
        response = client.get('/collection/personal/public')
        assert response.status_code == 200
        collections = list(response.context['object_list'])
        assert len(collections) == 0

        # Неавторизованный пользователь не может получить доступ
        response = client.get(f'/collection/personal/{collection_id}/list')
        assert response.status_code == 404

        # User2 не видит коллекцию в списке публичных
        client.force_login(user2)
        response = client.get('/collection/personal/public')
        assert response.status_code == 200
        collections = list(response.context['object_list'])
        assert len(collections) == 0

        # User2 не может получить доступ
        response = client.get(f'/collection/personal/{collection_id}/list')
        assert response.status_code == 404

        # User2 не может скопировать приватную коллекцию
        response = client.post(
            f'/api/collection/personal/{collection_id}/copy',
            content_type='application/json',
        )
        assert response.status_code == 403
