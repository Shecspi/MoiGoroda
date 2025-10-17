"""
Интеграционные тесты для API избранных коллекций.
"""

import pytest
from django.contrib.auth.models import User
from django.test import Client
from rest_framework import status

from collection.models import Collection, FavoriteCollection


@pytest.mark.django_db
@pytest.mark.integration
class TestFavoriteCollectionAPI:
    """Тесты для API favorite_collection_toggle."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    @pytest.fixture
    def user(self) -> User:
        """Создает тестового пользователя."""
        return User.objects.create_user(username='testuser', password='testpass123')

    @pytest.fixture
    def another_user(self) -> User:
        """Создает другого тестового пользователя."""
        return User.objects.create_user(username='anotheruser', password='testpass123')

    @pytest.fixture
    def collection(self) -> Collection:
        """Создает тестовую коллекцию."""
        return Collection.objects.create(title='Золотое кольцо')

    @pytest.fixture
    def another_collection(self) -> Collection:
        """Создает еще одну тестовую коллекцию."""
        return Collection.objects.create(title='Серебряное кольцо')

    def test_add_collection_to_favorites_success(
        self, client: Client, user: User, collection: Collection
    ) -> None:
        """Проверяет успешное добавление коллекции в избранное."""
        client.force_login(user)
        response = client.post(f'/api/collection/favorite/{collection.id}')

        assert response.status_code == status.HTTP_201_CREATED
        assert FavoriteCollection.objects.filter(user=user, collection=collection).exists()
        data = response.json()
        assert data['is_favorite'] is True

    def test_remove_collection_from_favorites_success(
        self, client: Client, user: User, collection: Collection
    ) -> None:
        """Проверяет успешное удаление коллекции из избранного."""
        # Сначала добавляем в избранное
        FavoriteCollection.objects.create(user=user, collection=collection)

        client.force_login(user)
        response = client.delete(f'/api/collection/favorite/{collection.id}')

        assert response.status_code == status.HTTP_200_OK
        assert not FavoriteCollection.objects.filter(user=user, collection=collection).exists()
        data = response.json()
        assert data['is_favorite'] is False

    def test_add_to_favorites_requires_authentication(
        self, client: Client, collection: Collection
    ) -> None:
        """Проверяет что добавление в избранное требует авторизации."""
        response = client.post(f'/api/collection/favorite/{collection.id}')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_remove_from_favorites_requires_authentication(
        self, client: Client, collection: Collection
    ) -> None:
        """Проверяет что удаление из избранного требует авторизации."""
        response = client.delete(f'/api/collection/favorite/{collection.id}')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_add_to_favorites_nonexistent_collection_returns_404(
        self, client: Client, user: User
    ) -> None:
        """Проверяет что добавление несуществующей коллекции возвращает 404."""
        client.force_login(user)
        response = client.post('/api/collection/favorite/99999')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_remove_from_favorites_nonexistent_collection_returns_404(
        self, client: Client, user: User
    ) -> None:
        """Проверяет что удаление несуществующей коллекции возвращает 404."""
        client.force_login(user)
        response = client.delete('/api/collection/favorite/99999')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_add_already_favorite_collection_returns_400(
        self, client: Client, user: User, collection: Collection
    ) -> None:
        """Проверяет что повторное добавление в избранное возвращает 400."""
        # Сначала добавляем в избранное
        FavoriteCollection.objects.create(user=user, collection=collection)

        client.force_login(user)
        response = client.post(f'/api/collection/favorite/{collection.id}')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert 'detail' in data

    def test_remove_not_favorite_collection_returns_400(
        self, client: Client, user: User, collection: Collection
    ) -> None:
        """Проверяет что удаление не избранной коллекции возвращает 400."""
        client.force_login(user)
        response = client.delete(f'/api/collection/favorite/{collection.id}')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert 'detail' in data

    def test_favorites_are_user_specific(
        self, client: Client, user: User, another_user: User, collection: Collection
    ) -> None:
        """Проверяет что избранное индивидуально для каждого пользователя."""
        # Пользователь 1 добавляет в избранное
        FavoriteCollection.objects.create(user=user, collection=collection)

        # Пользователь 2 может добавить ту же коллекцию в свое избранное
        client.force_login(another_user)
        response = client.post(f'/api/collection/favorite/{collection.id}')

        assert response.status_code == status.HTTP_201_CREATED
        assert FavoriteCollection.objects.filter(user=user, collection=collection).exists()
        assert FavoriteCollection.objects.filter(user=another_user, collection=collection).exists()

    def test_user_can_have_multiple_favorite_collections(
        self, client: Client, user: User, collection: Collection, another_collection: Collection
    ) -> None:
        """Проверяет что пользователь может иметь несколько избранных коллекций."""
        client.force_login(user)

        # Добавляем первую коллекцию
        response1 = client.post(f'/api/collection/favorite/{collection.id}')
        assert response1.status_code == status.HTTP_201_CREATED

        # Добавляем вторую коллекцию
        response2 = client.post(f'/api/collection/favorite/{another_collection.id}')
        assert response2.status_code == status.HTTP_201_CREATED

        # Проверяем что обе коллекции в избранном
        assert FavoriteCollection.objects.filter(user=user).count() == 2

    def test_only_post_and_delete_methods_allowed(
        self, client: Client, user: User, collection: Collection
    ) -> None:
        """Проверяет что разрешены только POST и DELETE методы."""
        client.force_login(user)

        # GET не разрешен
        response_get = client.get(f'/api/collection/favorite/{collection.id}')
        assert response_get.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        # PUT не разрешен
        response_put = client.put(f'/api/collection/favorite/{collection.id}')
        assert response_put.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        # PATCH не разрешен
        response_patch = client.patch(f'/api/collection/favorite/{collection.id}')
        assert response_patch.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
