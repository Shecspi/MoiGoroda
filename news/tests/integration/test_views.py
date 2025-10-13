"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any

from django.test import Client
from django.urls import reverse

from news.models import News


# ===== Integration тесты для NewsList =====


@pytest.mark.integration
@pytest.mark.django_db
def test_news_list_accessible_for_anonymous_user(client: Client) -> None:
    """Тест что страница новостей доступна для анонимного пользователя."""
    response = client.get(reverse('news-list'))

    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.django_db
def test_news_list_accessible_for_authenticated_user(
    client: Client, django_user_model: Any
) -> None:
    """Тест что страница новостей доступна для аутентифицированного пользователя."""
    user = django_user_model.objects.create_user(username='testuser', password='testpass')
    client.force_login(user)

    response = client.get(reverse('news-list'))

    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.django_db
def test_news_list_uses_correct_template(client: Client) -> None:
    """Тест что используется правильный шаблон."""
    response = client.get(reverse('news-list'))

    assert 'news/news__list.html' in [t.name for t in response.templates]


@pytest.mark.integration
@pytest.mark.django_db
def test_news_list_shows_news(client: Client) -> None:
    """Тест что новости отображаются на странице."""
    news1 = News.objects.create(title='News 1', content='Content 1')
    news2 = News.objects.create(title='News 2', content='Content 2')

    response = client.get(reverse('news-list'))

    assert response.status_code == 200
    assert news1 in response.context['object_list']
    assert news2 in response.context['object_list']


@pytest.mark.integration
@pytest.mark.django_db
def test_news_list_context_contains_required_keys(client: Client) -> None:
    """Тест что контекст содержит необходимые ключи."""
    response = client.get(reverse('news-list'))

    assert 'active_page' in response.context
    assert 'page_title' in response.context
    assert 'page_description' in response.context


@pytest.mark.integration
@pytest.mark.django_db
def test_news_list_context_values(client: Client) -> None:
    """Тест значений в контексте."""
    response = client.get(reverse('news-list'))

    assert response.context['active_page'] == 'news'
    assert response.context['page_title'] == 'Новости'
    assert response.context['page_description'] == 'Новости проекта «Мои города»'


@pytest.mark.integration
@pytest.mark.django_db
def test_news_list_pagination(client: Client) -> None:
    """Тест пагинации новостей."""
    # Создаем 10 новостей (больше чем paginate_by=5)
    for i in range(10):
        News.objects.create(title=f'News {i}', content=f'Content {i}')

    response = client.get(reverse('news-list'))

    assert response.status_code == 200
    assert 'page_obj' in response.context
    assert response.context['page_obj'].paginator.count == 10
    assert len(response.context['object_list']) == 5  # paginate_by


@pytest.mark.integration
@pytest.mark.django_db
def test_news_list_second_page(client: Client) -> None:
    """Тест второй страницы пагинации."""
    # Создаем 10 новостей
    for i in range(10):
        News.objects.create(title=f'News {i}', content=f'Content {i}')

    response = client.get(reverse('news-list') + '?page=2')

    assert response.status_code == 200
    assert len(response.context['object_list']) == 5


@pytest.mark.integration
@pytest.mark.django_db
def test_news_list_ordering(client: Client) -> None:
    """Тест сортировки новостей от новых к старым."""
    news1 = News.objects.create(title='First', content='Content 1')
    news2 = News.objects.create(title='Second', content='Content 2')
    news3 = News.objects.create(title='Third', content='Content 3')

    response = client.get(reverse('news-list'))

    object_list = list(response.context['object_list'])

    # Новости должны быть от новых к старым
    assert object_list[0] == news3
    assert object_list[1] == news2
    assert object_list[2] == news1


@pytest.mark.integration
@pytest.mark.django_db
def test_news_list_marks_news_as_read_for_authenticated_user(
    client: Client, django_user_model: Any
) -> None:
    """Тест что новости отмечаются прочитанными для аутентифицированного пользователя."""
    user = django_user_model.objects.create_user(username='testuser', password='testpass')
    news = News.objects.create(title='Test News', content='Test content')

    client.force_login(user)

    # До просмотра новость не прочитана
    assert news.users_read.count() == 0

    response = client.get(reverse('news-list'))

    assert response.status_code == 200

    # После просмотра новость прочитана
    news.refresh_from_db()
    assert news.users_read.count() == 1
    assert user in news.users_read.all()


@pytest.mark.integration
@pytest.mark.django_db
def test_news_list_does_not_mark_news_as_read_for_anonymous_user(client: Client) -> None:
    """Тест что новости НЕ отмечаются прочитанными для анонимного пользователя."""
    news = News.objects.create(title='Test News', content='Test content')

    response = client.get(reverse('news-list'))

    assert response.status_code == 200

    # Новость не должна быть прочитана
    news.refresh_from_db()
    assert news.users_read.count() == 0


@pytest.mark.integration
@pytest.mark.django_db
def test_news_list_marks_only_current_page_news_as_read(
    client: Client, django_user_model: Any
) -> None:
    """Тест что прочитанными отмечаются только новости текущей страницы."""
    user = django_user_model.objects.create_user(username='testuser', password='testpass')

    # Создаем 10 новостей
    all_news = []
    for i in range(10):
        news = News.objects.create(title=f'News {i}', content=f'Content {i}')
        all_news.append(news)

    client.force_login(user)

    # Смотрим первую страницу
    response = client.get(reverse('news-list'))

    assert response.status_code == 200

    # Должны быть прочитаны только 5 новостей (первая страница)
    read_count = sum(1 for news in all_news if user in news.users_read.all())
    assert read_count == 5


@pytest.mark.integration
@pytest.mark.django_db
def test_news_list_already_read_news_not_marked_again(
    client: Client, django_user_model: Any
) -> None:
    """Тест что уже прочитанные новости не отмечаются повторно."""
    user = django_user_model.objects.create_user(username='testuser', password='testpass')
    news = News.objects.create(title='Test News', content='Test content')

    # Отмечаем новость как прочитанную
    news.users_read.add(user)

    client.force_login(user)

    # Просматриваем страницу снова
    response = client.get(reverse('news-list'))

    assert response.status_code == 200

    # Новость все еще прочитана только один раз
    news.refresh_from_db()
    assert news.users_read.count() == 1


@pytest.mark.integration
@pytest.mark.django_db
def test_news_list_annotates_news_as_read_for_authenticated_user(
    client: Client, django_user_model: Any
) -> None:
    """Тест что новости аннотируются полем is_read для аутентифицированного пользователя."""
    user = django_user_model.objects.create_user(username='testuser', password='testpass')
    news1 = News.objects.create(title='Read News', content='Content 1')
    News.objects.create(title='Unread News', content='Content 2')  # Непрочитанная новость

    # Отмечаем одну новость как прочитанную
    news1.users_read.add(user)

    client.force_login(user)

    response = client.get(reverse('news-list'))

    # Проверяем что новости аннотированы
    object_list = response.context['object_list']
    # news2 отображается первым (новее)
    assert hasattr(object_list[0], 'is_read')
    assert hasattr(object_list[1], 'is_read')


@pytest.mark.integration
@pytest.mark.django_db
def test_news_list_shows_readers_count_for_superuser(
    client: Client, django_user_model: Any
) -> None:
    """Тест что для суперпользователя отображается количество прочитавших."""
    superuser = django_user_model.objects.create_superuser(username='admin', password='adminpass')
    user1 = django_user_model.objects.create_user(username='user1', password='pass1')
    user2 = django_user_model.objects.create_user(username='user2', password='pass2')

    news = News.objects.create(title='Test News', content='Test content')
    news.users_read.add(user1, user2)

    client.force_login(superuser)

    response = client.get(reverse('news-list'))

    # Проверяем что новость аннотирована количеством читателей
    object_list = response.context['object_list']
    assert hasattr(object_list[0], 'number_of_users_who_read_news')
    assert object_list[0].number_of_users_who_read_news == 2


@pytest.mark.integration
@pytest.mark.django_db
def test_news_list_does_not_show_readers_count_for_regular_user(
    client: Client, django_user_model: Any
) -> None:
    """Тест что для обычного пользователя не отображается количество прочитавших."""
    user = django_user_model.objects.create_user(username='testuser', password='testpass')
    News.objects.create(title='Test News', content='Test content')

    client.force_login(user)

    response = client.get(reverse('news-list'))

    # Для обычного пользователя не должно быть аннотации number_of_users_who_read_news
    object_list = response.context['object_list']
    assert not hasattr(object_list[0], 'number_of_users_who_read_news')


@pytest.mark.integration
@pytest.mark.django_db
def test_news_list_empty_list(client: Client) -> None:
    """Тест отображения пустого списка новостей."""
    response = client.get(reverse('news-list'))

    assert response.status_code == 200
    assert len(response.context['object_list']) == 0


@pytest.mark.integration
@pytest.mark.django_db
def test_news_list_url_resolves_correctly(client: Client) -> None:
    """Тест что URL новостей правильно разрешается."""
    News.objects.create(title='Test', content='Content')

    response = client.get('/news/')

    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.django_db
def test_news_list_with_different_users(client: Client, django_user_model: Any) -> None:
    """Тест что разные пользователи видят одинаковые новости."""
    user1 = django_user_model.objects.create_user(username='user1', password='pass1')
    user2 = django_user_model.objects.create_user(username='user2', password='pass2')

    news = News.objects.create(title='Test News', content='Test content')

    # Пользователь 1
    client.force_login(user1)
    response1 = client.get(reverse('news-list'))

    # Пользователь 2
    client.force_login(user2)
    response2 = client.get(reverse('news-list'))

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert news in response1.context['object_list']
    assert news in response2.context['object_list']


@pytest.mark.integration
@pytest.mark.django_db
def test_news_list_multiple_users_read_same_news(client: Client, django_user_model: Any) -> None:
    """Тест что несколько пользователей могут прочитать одну новость."""
    user1 = django_user_model.objects.create_user(username='user1', password='pass1')
    user2 = django_user_model.objects.create_user(username='user2', password='pass2')

    news = News.objects.create(title='Test News', content='Test content')

    # Пользователь 1 читает новость
    client.force_login(user1)
    client.get(reverse('news-list'))

    # Пользователь 2 читает новость
    client.force_login(user2)
    client.get(reverse('news-list'))

    news.refresh_from_db()
    assert news.users_read.count() == 2
    assert user1 in news.users_read.all()
    assert user2 in news.users_read.all()


@pytest.mark.integration
@pytest.mark.django_db
def test_news_list_pagination_preserves_context(client: Client) -> None:
    """Тест что пагинация сохраняет контекст."""
    # Создаем 10 новостей
    for i in range(10):
        News.objects.create(title=f'News {i}', content=f'Content {i}')

    response = client.get(reverse('news-list') + '?page=2')

    assert response.status_code == 200
    assert response.context['active_page'] == 'news'
    assert response.context['page_title'] == 'Новости'


@pytest.mark.integration
@pytest.mark.django_db
def test_news_list_invalid_page_number(client: Client) -> None:
    """Тест обработки некорректного номера страницы."""
    News.objects.create(title='Test', content='Content')

    response = client.get(reverse('news-list') + '?page=999')

    # Django возвращает 404 для несуществующей страницы
    assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.django_db
def test_news_list_marks_news_on_second_page_as_read(
    client: Client, django_user_model: Any
) -> None:
    """Тест что новости на второй странице также отмечаются прочитанными."""
    user = django_user_model.objects.create_user(username='testuser', password='testpass')

    # Создаем 10 новостей
    for i in range(10):
        News.objects.create(title=f'News {i}', content=f'Content {i}')

    client.force_login(user)

    # Смотрим вторую страницу
    response = client.get(reverse('news-list') + '?page=2')

    assert response.status_code == 200

    # Проверяем что новости со второй страницы прочитаны
    news_on_page = response.context['object_list']
    for news in news_on_page:
        assert user in news.users_read.all()
