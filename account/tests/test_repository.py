import pytest
from account.dto import SubscriberUserDTO, SubscribedUserDTO

from account.repository import (
    get_subscriber_users,
    get_subscribed_users,
)  # импортируем тестируемую функцию (пример пути)


@pytest.fixture
def mock_subscribe_qs(mocker):
    """Фикстура для мока Subscribe.objects.filter"""
    return mocker.patch('subscribe.models.Subscribe.objects.filter')


@pytest.fixture
def mock_share_settings_qs(mocker):
    """Фикстура для мока ShareSettings.objects.filter"""
    return mocker.patch('account.models.ShareSettings.objects.filter')


def test_get_subscriber_users_empty_list(mock_subscribe_qs):
    # Тест, если у пользователя нет подписчиков - должна вернуться пустая коллекция
    mock_subscribe_qs.return_value = []

    result = get_subscriber_users(user_id=1)
    assert result == []


def test_get_subscriber_users_with_subscribers_and_share_settings(
    mocker, mock_subscribe_qs, mock_share_settings_qs
):
    # Создадим мок-объекты для подписки и настроек
    subscriber_user = mocker.Mock()
    subscriber_user.id = 123
    subscriber_user.username = 'subscriber1'

    subscribe_instance = mocker.Mock()
    subscribe_instance.subscribe_from = subscriber_user

    mock_subscribe_qs.return_value = [subscribe_instance]

    share_setting_instance = mocker.Mock()
    share_setting_instance.can_share = True

    # Подменим ShareSettings.objects.filter
    share_qs_mock = mocker.Mock()
    share_qs_mock.exists.return_value = True
    share_qs_mock.first.return_value = share_setting_instance
    mock_share_settings_qs.return_value = share_qs_mock

    result = get_subscriber_users(user_id=1)

    assert len(result) == 1
    dto = result[0]
    assert isinstance(dto, SubscriberUserDTO)
    assert dto.id == subscriber_user.id
    assert dto.username == subscriber_user.username
    assert dto.can_subscribe is True


def test_get_subscriber_users_with_subscribers_but_no_share_settings(
    mocker, mock_subscribe_qs, mock_share_settings_qs
):
    subscriber_user = mocker.Mock()
    subscriber_user.id = 456
    subscriber_user.username = 'subscriber2'

    subscribe_instance = mocker.Mock()
    subscribe_instance.subscribe_from = subscriber_user

    mock_subscribe_qs.return_value = [subscribe_instance]

    # ShareSettings.objects.filter возвращает пустой queryset
    share_qs_mock = mocker.Mock()
    share_qs_mock.exists.return_value = False
    # first не должен вызываться, но если вызовется — пусть будет None
    share_qs_mock.first.return_value = None
    mock_share_settings_qs.return_value = share_qs_mock

    result = get_subscriber_users(user_id=2)

    assert len(result) == 1
    dto = result[0]
    assert isinstance(dto, SubscriberUserDTO)
    assert dto.id == subscriber_user.id
    assert dto.username == subscriber_user.username
    assert dto.can_subscribe is False


def test_get_subscriber_users_multiple_subscribers(
    mocker, mock_subscribe_qs, mock_share_settings_qs
):
    # Подписчики с разными настройками
    subscriber1 = mocker.Mock(id=1, username='user1')
    subscriber2 = mocker.Mock(id=2, username='user2')

    subscribe1 = mocker.Mock(subscribe_from=subscriber1)
    subscribe2 = mocker.Mock(subscribe_from=subscriber2)

    mock_subscribe_qs.return_value = [subscribe1, subscribe2]

    def share_settings_side_effect(user):
        share_qs_mock = mocker.Mock()
        if user.id == 1:
            share_qs_mock.exists.return_value = True
            share_qs_mock.first.return_value = mocker.Mock(can_share=True)
        else:
            share_qs_mock.exists.return_value = False
            share_qs_mock.first.return_value = None
        return share_qs_mock

    mock_share_settings_qs.side_effect = lambda **kwargs: share_settings_side_effect(kwargs['user'])

    result = get_subscriber_users(user_id=3)

    assert len(result) == 2

    dto1 = next(dto for dto in result if dto.id == subscriber1.id)
    assert dto1.can_subscribe is True

    dto2 = next(dto for dto in result if dto.id == subscriber2.id)
    assert dto2.can_subscribe is False


def test_get_subscribed_users_empty_list(mock_subscribe_qs):
    # Если у пользователя нет подписок - возвращается пустой список
    mock_subscribe_qs.return_value = []

    result = get_subscribed_users(user_id=1)
    assert result == []


def test_get_subscribed_users_single_item(mocker, mock_subscribe_qs):
    # Мокаем пользователя, на которого подписан текущий user_id
    subscribed_to_user = mocker.Mock()
    subscribed_to_user.id = 10
    subscribed_to_user.username = 'subscribed_user'

    subscribe_instance = mocker.Mock()
    subscribe_instance.subscribe_to = subscribed_to_user

    mock_subscribe_qs.return_value = [subscribe_instance]

    result = get_subscribed_users(user_id=1)

    assert len(result) == 1
    dto = result[0]
    assert isinstance(dto, SubscribedUserDTO)
    assert dto.id == 10
    assert dto.username == 'subscribed_user'


def test_get_subscribed_users_multiple_items(mocker, mock_subscribe_qs):
    # Несколько подписок у пользователя
    user1 = mocker.Mock(id=10, username='user1')
    user2 = mocker.Mock(id=20, username='user2')

    subscribe1 = mocker.Mock(subscribe_to=user1)
    subscribe2 = mocker.Mock(subscribe_to=user2)

    mock_subscribe_qs.return_value = [subscribe1, subscribe2]

    result = get_subscribed_users(user_id=42)

    assert len(result) == 2

    ids = {dto.id for dto in result}
    usernames = {dto.username for dto in result}

    assert ids == {10, 20}
    assert usernames == {'user1', 'user2'}
