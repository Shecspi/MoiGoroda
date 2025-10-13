"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any

from news.models import News
from news.repository import annotate_news_with_number_of_users_who_read_news


# ===== Unit тесты для repository =====


@pytest.mark.unit
@pytest.mark.django_db
def test_annotate_news_with_zero_readers() -> None:
    """Тест аннотации новости без прочитавших пользователей."""
    news = News.objects.create(title='Test News', content='Test content')

    annotated_news = annotate_news_with_number_of_users_who_read_news(
        News.objects.filter(id=news.id)
    ).first()

    assert annotated_news is not None
    assert annotated_news.number_of_users_who_read_news == 0  # type: ignore[attr-defined]


@pytest.mark.unit
@pytest.mark.django_db
def test_annotate_news_with_one_reader(django_user_model: Any) -> None:
    """Тест аннотации новости с одним прочитавшим пользователем."""
    user = django_user_model.objects.create_user(username='testuser', password='testpass')
    news = News.objects.create(title='Test News', content='Test content')
    news.users_read.add(user)

    annotated_news = annotate_news_with_number_of_users_who_read_news(
        News.objects.filter(id=news.id)
    ).first()

    assert annotated_news is not None
    assert annotated_news.number_of_users_who_read_news == 1  # type: ignore[attr-defined]


@pytest.mark.unit
@pytest.mark.django_db
def test_annotate_news_with_multiple_readers(django_user_model: Any) -> None:
    """Тест аннотации новости с несколькими прочитавшими пользователями."""
    user1 = django_user_model.objects.create_user(username='user1', password='pass1')
    user2 = django_user_model.objects.create_user(username='user2', password='pass2')
    user3 = django_user_model.objects.create_user(username='user3', password='pass3')

    news = News.objects.create(title='Test News', content='Test content')
    news.users_read.add(user1, user2, user3)

    annotated_news = annotate_news_with_number_of_users_who_read_news(
        News.objects.filter(id=news.id)
    ).first()

    assert annotated_news is not None
    assert annotated_news.number_of_users_who_read_news == 3  # type: ignore[attr-defined]


@pytest.mark.unit
@pytest.mark.django_db
def test_annotate_multiple_news_with_different_readers(django_user_model: Any) -> None:
    """Тест аннотации нескольких новостей с разным количеством читателей."""
    user1 = django_user_model.objects.create_user(username='user1', password='pass1')
    user2 = django_user_model.objects.create_user(username='user2', password='pass2')
    user3 = django_user_model.objects.create_user(username='user3', password='pass3')

    news1 = News.objects.create(title='News 1', content='Content 1')
    news2 = News.objects.create(title='News 2', content='Content 2')
    news3 = News.objects.create(title='News 3', content='Content 3')

    news1.users_read.add(user1)
    news2.users_read.add(user1, user2)
    news3.users_read.add(user1, user2, user3)

    annotated_news = annotate_news_with_number_of_users_who_read_news(News.objects.all())

    # Создаем словарь для проверки
    news_readers = {news.id: news.number_of_users_who_read_news for news in annotated_news}  # type: ignore[attr-defined]

    assert news_readers[news1.id] == 1
    assert news_readers[news2.id] == 2
    assert news_readers[news3.id] == 3


@pytest.mark.unit
@pytest.mark.django_db
def test_annotate_preserves_queryset_type() -> None:
    """Тест что аннотация сохраняет тип QuerySet."""
    News.objects.create(title='Test', content='Content')

    queryset = News.objects.all()
    annotated_queryset = annotate_news_with_number_of_users_who_read_news(queryset)

    assert annotated_queryset.model == News
    assert annotated_queryset.count() == 1


@pytest.mark.unit
@pytest.mark.django_db
def test_annotate_empty_queryset() -> None:
    """Тест аннотации пустого QuerySet."""
    annotated_queryset = annotate_news_with_number_of_users_who_read_news(News.objects.none())

    assert annotated_queryset.count() == 0


@pytest.mark.unit
@pytest.mark.django_db
def test_annotate_preserves_ordering() -> None:
    """Тест что аннотация сохраняет порядок сортировки."""
    news1 = News.objects.create(title='First', content='Content 1')
    news2 = News.objects.create(title='Second', content='Content 2')
    news3 = News.objects.create(title='Third', content='Content 3')

    # Используем фильтр для изоляции от других тестов
    test_ids = [news1.id, news2.id, news3.id]
    annotated_queryset = annotate_news_with_number_of_users_who_read_news(
        News.objects.filter(id__in=test_ids)
    )

    # Проверяем что все новости присутствуют и аннотация не нарушает queryset
    assert annotated_queryset.count() == 3

    # Проверяем что аннотация добавила нужное поле
    for news in annotated_queryset:
        assert hasattr(news, 'number_of_users_who_read_news')
        assert news.number_of_users_who_read_news == 0


@pytest.mark.unit
@pytest.mark.django_db
def test_annotate_with_filtered_queryset(django_user_model: Any) -> None:
    """Тест аннотации отфильтрованного QuerySet."""
    user = django_user_model.objects.create_user(username='testuser', password='testpass')

    news1 = News.objects.create(title='News 1', content='Content 1')
    News.objects.create(title='News 2', content='Content 2')  # Новость без читателей

    news1.users_read.add(user)

    # Фильтруем только новости с читателями
    filtered_queryset = News.objects.filter(users_read__isnull=False).distinct()
    annotated_news = list(annotate_news_with_number_of_users_who_read_news(filtered_queryset))

    assert len(annotated_news) == 1
    assert annotated_news[0].id == news1.id
    assert annotated_news[0].number_of_users_who_read_news == 1  # type: ignore[attr-defined]


@pytest.mark.unit
@pytest.mark.django_db
def test_annotate_news_after_adding_reader(django_user_model: Any) -> None:
    """Тест что аннотация обновляется после добавления читателя."""
    user = django_user_model.objects.create_user(username='testuser', password='testpass')
    news = News.objects.create(title='Test', content='Content')

    # До добавления читателя
    annotated_before = annotate_news_with_number_of_users_who_read_news(
        News.objects.filter(id=news.id)
    ).first()
    assert annotated_before is not None
    assert annotated_before.number_of_users_who_read_news == 0  # type: ignore[attr-defined]

    # Добавляем читателя
    news.users_read.add(user)

    # После добавления читателя
    annotated_after = annotate_news_with_number_of_users_who_read_news(
        News.objects.filter(id=news.id)
    ).first()
    assert annotated_after is not None
    assert annotated_after.number_of_users_who_read_news == 1  # type: ignore[attr-defined]


@pytest.mark.unit
@pytest.mark.django_db
def test_annotate_news_after_removing_reader(django_user_model: Any) -> None:
    """Тест что аннотация обновляется после удаления читателя."""
    user = django_user_model.objects.create_user(username='testuser', password='testpass')
    news = News.objects.create(title='Test', content='Content')
    news.users_read.add(user)

    # До удаления читателя
    annotated_before = annotate_news_with_number_of_users_who_read_news(
        News.objects.filter(id=news.id)
    ).first()
    assert annotated_before is not None
    assert annotated_before.number_of_users_who_read_news == 1  # type: ignore[attr-defined]

    # Удаляем читателя
    news.users_read.remove(user)

    # После удаления читателя
    annotated_after = annotate_news_with_number_of_users_who_read_news(
        News.objects.filter(id=news.id)
    ).first()
    assert annotated_after is not None
    assert annotated_after.number_of_users_who_read_news == 0  # type: ignore[attr-defined]


@pytest.mark.unit
@pytest.mark.django_db
def test_annotate_same_user_reads_multiple_news(django_user_model: Any) -> None:
    """Тест аннотации когда один пользователь читает несколько новостей."""
    user = django_user_model.objects.create_user(username='testuser', password='testpass')

    news1 = News.objects.create(title='News 1', content='Content 1')
    news2 = News.objects.create(title='News 2', content='Content 2')
    news3 = News.objects.create(title='News 3', content='Content 3')

    news1.users_read.add(user)
    news2.users_read.add(user)
    news3.users_read.add(user)

    annotated_news = list(annotate_news_with_number_of_users_who_read_news(News.objects.all()))

    # Все новости должны иметь одного читателя
    for news in annotated_news:
        assert news.number_of_users_who_read_news == 1  # type: ignore[attr-defined]
