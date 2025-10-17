"""
Интеграционные тесты для модели FavoriteCollection.
Тесты проверяют взаимодействие с базой данных.
"""

import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError

from collection.models import Collection, FavoriteCollection


@pytest.mark.django_db
@pytest.mark.integration
class TestFavoriteCollectionModelIntegration:
    """Интеграционные тесты для модели FavoriteCollection (с БД)."""

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

    def test_create_and_save_favorite_collection(self, user: User, collection: Collection) -> None:
        """Проверяет создание и сохранение избранной коллекции в БД."""
        favorite = FavoriteCollection.objects.create(user=user, collection=collection)

        assert favorite.id is not None
        assert favorite.user == user
        assert favorite.collection == collection
        assert favorite.created_at is not None

        # Проверяем что запись существует в БД
        saved_favorite = FavoriteCollection.objects.get(id=favorite.id)
        assert saved_favorite.user == user
        assert saved_favorite.collection == collection

    def test_str_representation(self, user: User, collection: Collection) -> None:
        """Проверяет метод __str__ модели."""
        favorite = FavoriteCollection.objects.create(user=user, collection=collection)

        expected_str = f'{user.username} - {collection.title}'
        assert str(favorite) == expected_str

    def test_unique_together_constraint(self, user: User, collection: Collection) -> None:
        """Проверяет unique_together constraint на уровне БД."""
        FavoriteCollection.objects.create(user=user, collection=collection)

        with pytest.raises(IntegrityError):
            FavoriteCollection.objects.create(user=user, collection=collection)

    def test_different_users_can_favorite_same_collection(
        self, user: User, another_user: User, collection: Collection
    ) -> None:
        """Проверяет что разные пользователи могут добавить одну коллекцию."""
        favorite1 = FavoriteCollection.objects.create(user=user, collection=collection)
        favorite2 = FavoriteCollection.objects.create(user=another_user, collection=collection)

        assert favorite1.id != favorite2.id
        assert FavoriteCollection.objects.filter(collection=collection).count() == 2

    def test_user_can_have_multiple_favorites(self, user: User) -> None:
        """Проверяет что пользователь может иметь несколько избранных."""
        collection1 = Collection.objects.create(title='Золотое кольцо')
        collection2 = Collection.objects.create(title='Серебряное кольцо')
        collection3 = Collection.objects.create(title='Столицы регионов')

        FavoriteCollection.objects.create(user=user, collection=collection1)
        FavoriteCollection.objects.create(user=user, collection=collection2)
        FavoriteCollection.objects.create(user=user, collection=collection3)

        assert FavoriteCollection.objects.filter(user=user).count() == 3

    def test_cascade_delete_on_user_deletion(self, user: User, collection: Collection) -> None:
        """Проверяет CASCADE при удалении пользователя."""
        favorite = FavoriteCollection.objects.create(user=user, collection=collection)
        favorite_id = favorite.id

        user.delete()

        assert not FavoriteCollection.objects.filter(id=favorite_id).exists()

    def test_cascade_delete_on_collection_deletion(
        self, user: User, collection: Collection
    ) -> None:
        """Проверяет CASCADE при удалении коллекции."""
        favorite = FavoriteCollection.objects.create(user=user, collection=collection)
        favorite_id = favorite.id

        collection.delete()

        assert not FavoriteCollection.objects.filter(id=favorite_id).exists()

    def test_ordering_by_created_at_desc(self, user: User) -> None:
        """Проверяет сортировку по дате создания (новые первые)."""
        collection1 = Collection.objects.create(title='Первая')
        collection2 = Collection.objects.create(title='Вторая')
        collection3 = Collection.objects.create(title='Третья')

        favorite1 = FavoriteCollection.objects.create(user=user, collection=collection1)
        favorite2 = FavoriteCollection.objects.create(user=user, collection=collection2)
        favorite3 = FavoriteCollection.objects.create(user=user, collection=collection3)

        favorites = list(FavoriteCollection.objects.filter(user=user))

        # Последняя созданная должна быть первой (ordering = ['-created_at'])
        assert favorites[0].id == favorite3.id
        assert favorites[1].id == favorite2.id
        assert favorites[2].id == favorite1.id

    def test_related_name_favorite_collections(self, user: User, collection: Collection) -> None:
        """Проверяет related_name='favorite_collections' для User."""
        FavoriteCollection.objects.create(user=user, collection=collection)

        assert user.favorite_collections.count() == 1
        first_favorite = user.favorite_collections.first()
        assert first_favorite is not None
        assert first_favorite.collection == collection

    def test_related_name_favorited_by(
        self, user: User, another_user: User, collection: Collection
    ) -> None:
        """Проверяет related_name='favorited_by' для Collection."""
        FavoriteCollection.objects.create(user=user, collection=collection)
        FavoriteCollection.objects.create(user=another_user, collection=collection)

        assert collection.favorited_by.count() == 2
        favorited_users = [fav.user for fav in collection.favorited_by.all()]
        assert user in favorited_users
        assert another_user in favorited_users

    def test_filter_favorites_by_user(self, user: User, another_user: User) -> None:
        """Проверяет фильтрацию избранного по пользователю."""
        collection1 = Collection.objects.create(title='Коллекция 1')
        collection2 = Collection.objects.create(title='Коллекция 2')
        collection3 = Collection.objects.create(title='Коллекция 3')

        FavoriteCollection.objects.create(user=user, collection=collection1)
        FavoriteCollection.objects.create(user=user, collection=collection2)
        FavoriteCollection.objects.create(user=another_user, collection=collection3)

        user_favorites = FavoriteCollection.objects.filter(user=user)
        assert user_favorites.count() == 2

        another_user_favorites = FavoriteCollection.objects.filter(user=another_user)
        assert another_user_favorites.count() == 1
