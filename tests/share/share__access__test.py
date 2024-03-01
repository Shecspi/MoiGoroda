import pytest
from django.urls import reverse

from tests.share.conftest import create_permissions_in_db


@pytest.mark.django_db
@pytest.mark.parametrize(
    'username, password, requested_user_id, status_code', (
        (None, None, 999, 404),
        ('username1', 'password', 999, 404),
        ('username2', 'password', 999, 404)
    )
)
def test__access__not_existing_user(setup, client, username, password, requested_user_id, status_code):
    """
    При попытке просмотра статистики неуществующего пользователя должна возвращаться ошибка 404.
    """
    if not username and not password:
        client.login(username=username, password=password)
    response = client.get(reverse('share', kwargs={'pk': requested_user_id}))

    assert response.status_code == status_code


@pytest.mark.django_db
@pytest.mark.parametrize(
    'username, password, requested_user_id, status_code', (
        (None, None, 1, 404),
        ('username1', 'password', 1, 404),
        ('username2', 'password', 1, 404)
    )
)
def test__access__has_no_permissions_without_db_entry(
        setup, client, username, password, requested_user_id, status_code
):
    """
    Если пользователь ни разу не применял настройки "Поделиться статистикой",
    то по-умолчанию его статистика не доступна к просмотру никому.
    При просмотре своей статистики действуют те же ограничения, что и для всех.
    """
    if not username and not password:
        client.login(username=username, password=password)
    response = client.get(reverse('share', kwargs={'pk': requested_user_id}))

    assert response.status_code == status_code


@pytest.mark.django_db
@pytest.mark.parametrize(
    'settings, requested_page, status_code, redirect_page', (
        # Если основная настройка False или все три вспомогательные False,
        # то при заходе на любую страницу должен быть ответ 404.
        ((False, False, False, False), '', 404, None),
        ((True, False, False, False), '', 404, None),
        ((False, True, False, False), '', 404, None),
        ((False, False, True, False), '', 404, None),
        ((False, False, False, True), '', 404, None),
        ((False, False, False, False), 'city_map', 404, None),
        ((True, False, False, False), 'city_map', 404, None),
        ((False, True, False, False), 'city_map', 404, None),
        ((False, False, True, False), 'city_map', 404, None),
        ((False, False, False, True), 'city_map', 404, None),
        ((False, False, False, False), 'region_map', 404, None),
        ((True, False, False, False), 'region_map', 404, None),
        ((False, True, False, False), 'region_map', 404, None),
        ((False, False, True, False), 'region_map', 404, None),
        ((False, False, False, True), 'region_map', 404, None),

        # Если основная настройка True и пытаемся зайти на ту страницу, которая в БД True,
        # то ответ должен быть 200. Если же на искомой странице False, то должно происходить
        # перенаправление на следующую по приоритетности страницу.
        ((True, True, False, False), '', 200, None),  # Все ок, открываем страницу dashboard
        ((True, False, True, False), '', 302, 'city_map'),  # dashboard не доступен, должно быть перенаправление на city_map
        ((True, False, False, True), '', 302, 'region_map'),  # dashboard не доступен, должно быть перенаправление на region_map
        ((True, True, False, False), 'city_map', 302, 'dashboard'),  # city_map не доступна, должно быть перенаправление на dashboard
        ((True, False, True, False), 'city_map', 200, None),  # Все ок, открываем страницу city_map
        ((True, False, False, True), 'city_map', 302, 'region_map'),  # city_map не доступна, должно быть перенаправление на regino_map
        ((True, True, False, False), 'region_map', 302, 'dashboard'),  # region_map не доступна, должно быть перенаправление на dashboard
        ((True, False, True, False), 'region_map', 302, 'city_map'),  # region_map не доступна, должно быть перенаправление на city_map
        ((True, False, False, True), 'region_map', 200, None),  # Все ок, открываем страницу region_map
    )
)
def test__access_has_no_permissions_with_db_entry(setup, client, settings, requested_page, status_code, redirect_page):
    create_permissions_in_db(1, settings)
    if requested_page:
        response = client.get(reverse('share', kwargs={'pk': 1, 'requested_page': requested_page}))
    else:
        response = client.get(reverse('share', kwargs={'pk': 1}))

    assert response.status_code == status_code

    if redirect_page:
        if requested_page:
            response = client.get(reverse('share', kwargs={'pk': 1, 'requested_page': requested_page}), follow=True)
        else:
            response = client.get(reverse('share', kwargs={'pk': 1}), follow=True)
        assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize(
    'requested_page, status_code', (
        ('', 200),
        ('city_map', 200),
        ('region_map', 200),
        ('sdfsdf', 404)
    )
)
def test__requested_page(setup, client, requested_page, status_code):
    create_permissions_in_db(1, (True, True, True, True))
    if requested_page:
        response = client.get(reverse('share', kwargs={'pk': 1, 'requested_page': requested_page}))
    else:
        response = client.get(reverse('share', kwargs={'pk': 1}))

    assert response.status_code == status_code
