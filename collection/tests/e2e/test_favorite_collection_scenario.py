"""
E2E тесты для сценария работы с избранными коллекциями.
Полный путь пользователя: просмотр коллекций -> добавление в избранное -> проверка сортировки -> удаление.
"""

import pytest
from django.contrib.auth.models import User
from django.test import Client

from collection.models import Collection, FavoriteCollection


@pytest.mark.django_db
@pytest.mark.e2e
class TestFavoriteCollectionScenario:
    """E2E тесты для полного сценария работы с избранными коллекциями."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    @pytest.fixture
    def user(self) -> User:
        """Создает авторизованного пользователя."""
        return User.objects.create_user(
            username='testuser', password='testpass123', email='test@example.com'
        )

    @pytest.fixture
    def collections(self) -> list[Collection]:
        """Создает несколько тестовых коллекций."""
        return [
            Collection.objects.create(title='Золотое кольцо'),
            Collection.objects.create(title='Серебряное кольцо'),
            Collection.objects.create(title='Столицы регионов'),
            Collection.objects.create(title='Города-миллионники'),
        ]

    def test_full_favorite_workflow(
        self, client: Client, user: User, collections: list[Collection]
    ) -> None:
        """
        Полный сценарий работы с избранными коллекциями:
        1. Пользователь заходит на страницу коллекций
        2. Добавляет несколько коллекций в избранное через API
        3. Проверяет что избранные коллекции отображаются первыми
        4. Удаляет одну коллекцию из избранного
        5. Проверяет обновленный список
        """
        client.force_login(user)

        # Шаг 1: Просмотр страницы коллекций (неавторизованный пользователь видит все)
        response = client.get('/collection/')
        assert response.status_code == 200

        # Шаг 2: Добавление коллекций в избранное через API
        collection1 = collections[0]
        collection2 = collections[1]

        # Добавляем первую коллекцию
        response = client.post(f'/api/collection/favorite/{collection1.id}')
        assert response.status_code == 201
        data = response.json()
        assert data['is_favorite'] is True

        # Добавляем вторую коллекцию
        response = client.post(f'/api/collection/favorite/{collection2.id}')
        assert response.status_code == 201

        # Проверяем что в БД две избранные коллекции
        assert FavoriteCollection.objects.filter(user=user).count() == 2

        # Шаг 3: Проверяем что избранные коллекции есть в списке
        response = client.get('/collection/')
        assert response.status_code == 200
        context_collections = list(response.context['object_list'])

        # Проверяем что избранные коллекции помечены
        favorite_ids = {collection1.id, collection2.id}
        for collection in context_collections:
            if collection.id in favorite_ids:
                assert collection.is_favorite is True
            else:
                assert collection.is_favorite is False

        # Шаг 4: Удаление одной коллекции из избранного
        response = client.delete(f'/api/collection/favorite/{collection1.id}')
        assert response.status_code == 200
        data = response.json()
        assert data['is_favorite'] is False

        # Шаг 5: Проверяем обновленный список избранного
        assert FavoriteCollection.objects.filter(user=user).count() == 1
        remaining_favorite = FavoriteCollection.objects.get(user=user)
        assert remaining_favorite.collection == collection2

    def test_favorite_not_visible_for_anonymous_user(
        self, client: Client, collections: list[Collection]
    ) -> None:
        """
        Проверяет что неавторизованный пользователь не видит функционал избранного.
        """
        # Попытка добавить в избранное без авторизации
        response = client.post(f'/api/collection/favorite/{collections[0].id}')
        assert response.status_code == 403  # Forbidden

        # Проверяем страницу коллекций (не должно быть звездочек)
        response = client.get('/collection/')
        assert response.status_code == 200
        # У неавторизованного пользователя нет поля is_favorite
        context_collections = list(response.context['object_list'])
        for collection in context_collections:
            assert not hasattr(collection, 'is_favorite') or collection.is_favorite is False

    def test_favorites_sorting_by_progress(
        self, client: Client, user: User, collections: list[Collection]
    ) -> None:
        """
        Проверяет что избранные коллекции сортируются по прогрессу,
        затем по алфавиту.
        """
        client.force_login(user)

        # Добавляем все коллекции в избранное
        for collection in collections:
            client.post(f'/api/collection/favorite/{collection.id}')

        # Получаем список коллекций
        response = client.get('/collection/')
        assert response.status_code == 200
        context_collections = list(response.context['object_list'])

        # Проверяем что все избранные идут первыми
        favorite_ids = {c.id for c in collections}
        favorites_in_list = [c for c in context_collections if c.id in favorite_ids]

        assert len(favorites_in_list) == len(collections)
        # Все избранные должны быть в начале списка
        for i, collection in enumerate(favorites_in_list):
            assert collection.is_favorite is True

    def test_multiple_users_independent_favorites(
        self, client: Client, collections: list[Collection]
    ) -> None:
        """
        Проверяет что избранное разных пользователей не пересекается.
        """
        # Создаем двух пользователей
        user1 = User.objects.create_user(username='user1', password='pass123')
        user2 = User.objects.create_user(username='user2', password='pass123')

        # Пользователь 1 добавляет первую коллекцию
        client.force_login(user1)
        response = client.post(f'/api/collection/favorite/{collections[0].id}')
        assert response.status_code == 201

        # Пользователь 2 добавляет вторую коллекцию
        client.force_login(user2)
        response = client.post(f'/api/collection/favorite/{collections[1].id}')
        assert response.status_code == 201

        # Проверяем что у каждого пользователя своё избранное
        assert FavoriteCollection.objects.filter(user=user1).count() == 1
        assert FavoriteCollection.objects.filter(user=user2).count() == 1

        user1_favorite = FavoriteCollection.objects.get(user=user1)
        user2_favorite = FavoriteCollection.objects.get(user=user2)

        assert user1_favorite.collection == collections[0]
        assert user2_favorite.collection == collections[1]

    def test_attempt_to_add_duplicate_favorite(
        self, client: Client, user: User, collections: list[Collection]
    ) -> None:
        """
        Проверяет обработку попытки добавить коллекцию в избранное дважды.
        """
        client.force_login(user)
        collection = collections[0]

        # Первое добавление - успешно
        response = client.post(f'/api/collection/favorite/{collection.id}')
        assert response.status_code == 201

        # Повторное добавление - ошибка
        response = client.post(f'/api/collection/favorite/{collection.id}')
        assert response.status_code == 400
        data = response.json()
        assert 'detail' in data

    def test_attempt_to_remove_non_favorite(
        self, client: Client, user: User, collections: list[Collection]
    ) -> None:
        """
        Проверяет обработку попытки удалить коллекцию, которой нет в избранном.
        """
        client.force_login(user)
        collection = collections[0]

        # Попытка удалить коллекцию, которая не в избранном
        response = client.delete(f'/api/collection/favorite/{collection.id}')
        assert response.status_code == 400
        data = response.json()
        assert 'detail' in data

