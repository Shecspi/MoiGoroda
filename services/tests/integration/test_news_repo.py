"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any

from services.db.news_repo import annotate_news_as_read
from news.models import News


@pytest.mark.integration
@pytest.mark.django_db
def test_annotate_news_as_read_adds_is_read_field(django_user_model: Any) -> None:
    """Тест что annotate_news_as_read добавляет поле is_read"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    # Создаём новость
    News.objects.create(title='Test News', content='Test content')

    # Получаем QuerySet и добавляем аннотацию
    queryset = News.objects.all()
    result = annotate_news_as_read(queryset, user.id)

    # Проверяем, что поле is_read добавлено
    first_news = result.first()
    assert hasattr(first_news, 'is_read')


@pytest.mark.integration
@pytest.mark.django_db
def test_annotate_news_as_read_returns_queryset(django_user_model: Any) -> None:
    """Тест что annotate_news_as_read возвращает QuerySet"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    News.objects.create(title='Test News', content='Test content')

    queryset = News.objects.all()
    result = annotate_news_as_read(queryset, user.id)

    assert result is not None


@pytest.mark.integration
@pytest.mark.django_db
def test_annotate_news_as_read_is_read_false_for_unread(django_user_model: Any) -> None:
    """Тест что is_read = False для непрочитанной новости"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    News.objects.create(title='Test News', content='Test content')

    queryset = News.objects.all()
    result = annotate_news_as_read(queryset, user.id)

    first_news = result.first()
    assert first_news is not None
    assert first_news.is_read is False  # type: ignore[attr-defined]


@pytest.mark.integration
@pytest.mark.django_db
def test_annotate_news_as_read_is_read_true_for_read(django_user_model: Any) -> None:
    """Тест что is_read = True для прочитанной новости"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    news = News.objects.create(title='Test News', content='Test content')
    news.users_read.add(user)

    queryset = News.objects.all()
    result = annotate_news_as_read(queryset, user.id)

    first_news = result.first()
    assert first_news is not None
    assert first_news.is_read is True  # type: ignore[attr-defined]


@pytest.mark.integration
@pytest.mark.django_db
def test_annotate_news_as_read_multiple_news(django_user_model: Any) -> None:
    """Тест что annotate_news_as_read работает с несколькими новостями"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    news1 = News.objects.create(title='News 1', content='Content 1')
    news2 = News.objects.create(title='News 2', content='Content 2')
    news3 = News.objects.create(title='News 3', content='Content 3')

    # Пользователь прочитал только news1 и news3
    news1.users_read.add(user)
    news3.users_read.add(user)

    queryset = News.objects.all()
    result = annotate_news_as_read(queryset, user.id)

    # Проверяем, что все новости имеют поле is_read
    for news in result:
        assert hasattr(news, 'is_read')

    # Проверяем значения is_read
    news_dict = {news.id: news.is_read for news in result}  # type: ignore[attr-defined]
    assert news_dict[news1.id] is True
    assert news_dict[news2.id] is False
    assert news_dict[news3.id] is True


@pytest.mark.integration
@pytest.mark.django_db
def test_annotate_news_as_read_different_users(django_user_model: Any) -> None:
    """Тест что annotate_news_as_read корректно работает с разными пользователями"""
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')

    news = News.objects.create(title='Test News', content='Test content')
    news.users_read.add(user1)

    queryset = News.objects.all()

    # Проверяем для user1
    result1 = annotate_news_as_read(queryset, user1.id)
    first1 = result1.first()
    assert first1 is not None
    assert first1.is_read is True  # type: ignore[attr-defined]

    # Проверяем для user2
    result2 = annotate_news_as_read(queryset, user2.id)
    first2 = result2.first()
    assert first2 is not None
    assert first2.is_read is False  # type: ignore[attr-defined]
