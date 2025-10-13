"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any

from django.utils import timezone

from news.models import News


# ===== Unit тесты для модели News =====


@pytest.mark.unit
@pytest.mark.django_db
def test_news_creation() -> None:
    """Тест создания новости."""
    news = News.objects.create(title='Test News', content='Test content')

    assert news.title == 'Test News'
    assert news.content == 'Test content'
    assert news.id is not None


@pytest.mark.unit
@pytest.mark.django_db
def test_news_has_all_required_fields() -> None:
    """Тест что модель News имеет все обязательные поля."""
    news = News.objects.create(title='News Title', content='News Content')

    assert hasattr(news, 'id')
    assert hasattr(news, 'title')
    assert hasattr(news, 'content')
    assert hasattr(news, 'created')
    assert hasattr(news, 'last_modified')
    assert hasattr(news, 'users_read')


@pytest.mark.unit
@pytest.mark.django_db
def test_news_str_representation() -> None:
    """Тест строкового представления модели News."""
    news = News.objects.create(title='Test Title', content='Test Content')

    assert str(news) == 'Test Title'


@pytest.mark.unit
@pytest.mark.django_db
def test_news_created_auto_now_add() -> None:
    """Тест что поле created автоматически устанавливается при создании."""
    before_creation = timezone.now()
    news = News.objects.create(title='Test', content='Content')
    after_creation = timezone.now()

    assert news.created is not None
    assert before_creation <= news.created <= after_creation


@pytest.mark.unit
@pytest.mark.django_db
def test_news_last_modified_auto_now() -> None:
    """Тест что поле last_modified обновляется автоматически."""
    news = News.objects.create(title='Test', content='Content')
    original_modified = news.last_modified

    # Обновляем новость
    news.title = 'Updated Title'
    news.save()
    news.refresh_from_db()

    assert news.last_modified > original_modified


@pytest.mark.unit
@pytest.mark.django_db
def test_news_users_read_many_to_many(django_user_model: Any) -> None:
    """Тест связи ManyToMany с пользователями."""
    user1 = django_user_model.objects.create_user(username='user1', password='pass1')
    user2 = django_user_model.objects.create_user(username='user2', password='pass2')

    news = News.objects.create(title='Test', content='Content')
    news.users_read.add(user1, user2)

    assert news.users_read.count() == 2
    assert user1 in news.users_read.all()
    assert user2 in news.users_read.all()


@pytest.mark.unit
@pytest.mark.django_db
def test_news_users_read_can_be_empty() -> None:
    """Тест что users_read может быть пустым."""
    news = News.objects.create(title='Test', content='Content')

    assert news.users_read.count() == 0


@pytest.mark.unit
@pytest.mark.django_db
def test_news_ordering() -> None:
    """Тест что новости сортируются по дате создания (от новых к старым)."""
    news1 = News.objects.create(title='First', content='Content 1')
    news2 = News.objects.create(title='Second', content='Content 2')
    news3 = News.objects.create(title='Third', content='Content 3')

    all_news = list(News.objects.all())

    # Новости должны быть отсортированы от новых к старым
    assert all_news[0] == news3
    assert all_news[1] == news2
    assert all_news[2] == news1


@pytest.mark.unit
@pytest.mark.django_db
def test_news_verbose_name() -> None:
    """Тест verbose_name модели."""
    assert News._meta.verbose_name == 'Новость'


@pytest.mark.unit
@pytest.mark.django_db
def test_news_verbose_name_plural() -> None:
    """Тест verbose_name_plural модели."""
    assert News._meta.verbose_name_plural == 'Новости'


@pytest.mark.unit
@pytest.mark.django_db
def test_news_title_max_length() -> None:
    """Тест максимальной длины поля title."""
    title_field = News._meta.get_field('title')
    assert title_field.max_length == 256


@pytest.mark.unit
@pytest.mark.django_db
def test_news_title_cannot_be_blank() -> None:
    """Тест что поле title не может быть пустым."""
    title_field = News._meta.get_field('title')
    assert title_field.blank is False
    assert title_field.null is False


@pytest.mark.unit
@pytest.mark.django_db
def test_news_content_cannot_be_blank() -> None:
    """Тест что поле content не может быть пустым."""
    content_field = News._meta.get_field('content')
    assert content_field.blank is False  # type: ignore[union-attr]
    assert content_field.null is False  # type: ignore[union-attr]


@pytest.mark.unit
@pytest.mark.django_db
def test_news_users_read_can_be_blank() -> None:
    """Тест что поле users_read может быть пустым."""
    users_read_field = News._meta.get_field('users_read')
    assert users_read_field.blank is True


@pytest.mark.unit
@pytest.mark.django_db
def test_news_remove_user_from_users_read(django_user_model: Any) -> None:
    """Тест удаления пользователя из users_read."""
    user = django_user_model.objects.create_user(username='testuser', password='testpass')
    news = News.objects.create(title='Test', content='Content')

    news.users_read.add(user)
    assert news.users_read.count() == 1

    news.users_read.remove(user)
    assert news.users_read.count() == 0


@pytest.mark.unit
@pytest.mark.django_db
def test_news_with_long_title() -> None:
    """Тест создания новости с длинным заголовком."""
    long_title = 'A' * 256
    news = News.objects.create(title=long_title, content='Content')

    assert news.title == long_title
    assert len(news.title) == 256


@pytest.mark.unit
@pytest.mark.django_db
def test_news_with_long_content() -> None:
    """Тест создания новости с длинным содержимым."""
    long_content = 'B' * 10000
    news = News.objects.create(title='Title', content=long_content)

    assert news.content == long_content
    assert len(news.content) == 10000


@pytest.mark.unit
@pytest.mark.django_db
def test_news_deletion() -> None:
    """Тест удаления новости."""
    news = News.objects.create(title='Test', content='Content')
    news_id = news.id

    news.delete()

    assert not News.objects.filter(id=news_id).exists()


@pytest.mark.unit
@pytest.mark.django_db
def test_news_update() -> None:
    """Тест обновления новости."""
    news = News.objects.create(title='Original Title', content='Original Content')

    news.title = 'Updated Title'
    news.content = 'Updated Content'
    news.save()

    news.refresh_from_db()

    assert news.title == 'Updated Title'
    assert news.content == 'Updated Content'


@pytest.mark.unit
@pytest.mark.django_db
def test_multiple_news_creation() -> None:
    """Тест создания нескольких новостей."""
    News.objects.create(title='News 1', content='Content 1')
    News.objects.create(title='News 2', content='Content 2')
    News.objects.create(title='News 3', content='Content 3')

    assert News.objects.count() == 3
    assert News.objects.filter(title='News 1').exists()
    assert News.objects.filter(title='News 2').exists()
    assert News.objects.filter(title='News 3').exists()
