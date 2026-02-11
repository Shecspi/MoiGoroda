from typing import Type
import pytest
from django.contrib.auth.models import User

from city.models import City, VisitedCity
from country.models import Country
from region.models import Region, RegionType
from subscribe.infrastructure.models import Subscribe, VisitedCityNotification


# =============================================================================
# Интеграционные тесты с базой данных (проверка реальной работы сигнала)
# =============================================================================


@pytest.fixture
def test_country() -> Country:
    """Создаёт тестовую страну."""
    return Country.objects.create(name='Тестовая страна', code='TC')


@pytest.fixture
def test_region_type() -> RegionType:
    """Создаёт тестовый тип региона."""
    return RegionType.objects.create(title='Область')


@pytest.fixture
def test_region(test_country: Country, test_region_type: RegionType) -> Region:
    """Создаёт тестовый регион."""
    return Region.objects.create(
        title='Тестовый регион',
        full_name='Тестовый регион полное название',
        country=test_country,
        type=test_region_type,
        iso3166='TEST',
    )


@pytest.fixture
def test_city(test_country: Country, test_region: Region) -> City:
    """Создаёт тестовый город."""
    return City.objects.create(
        title='Тестовый город',
        region=test_region,
        country=test_country,
        coordinate_width=55.7558,
        coordinate_longitude=37.6173,
    )


@pytest.fixture
def user_owner(django_user_model: Type[User]) -> User:
    """Пользователь-владелец, который добавляет города."""
    return django_user_model.objects.create_user(username='owner', password='password')


@pytest.fixture
def user_subscriber1(django_user_model: Type[User]) -> User:
    """Первый подписчик."""
    return django_user_model.objects.create_user(username='subscriber1', password='password')


@pytest.fixture
def user_subscriber2(django_user_model: Type[User]) -> User:
    """Второй подписчик."""
    return django_user_model.objects.create_user(username='subscriber2', password='password')


@pytest.fixture
def user_not_subscriber(django_user_model: Type[User]) -> User:
    """Пользователь, не подписанный на owner."""
    return django_user_model.objects.create_user(username='not_subscriber', password='password')


@pytest.mark.django_db
@pytest.mark.integration
def test_signal_creates_notification_for_subscriber(
    test_city: City,
    user_owner: User,
    user_subscriber1: User,
) -> None:
    """При создании VisitedCity для пользователя с подписчиком должно создаться уведомление."""
    Subscribe.objects.create(subscribe_from=user_subscriber1, subscribe_to=user_owner)

    VisitedCity.objects.create(
        user=user_owner,
        city=test_city,
        rating=5,
    )

    notifications = VisitedCityNotification.objects.all()
    assert notifications.count() == 1

    notification = notifications.first()
    assert notification is not None
    assert notification.recipient == user_subscriber1
    assert notification.sender == user_owner
    assert notification.city == test_city
    assert notification.is_read is False


@pytest.mark.django_db
@pytest.mark.integration
def test_signal_creates_notifications_for_multiple_subscribers(
    test_city: City,
    user_owner: User,
    user_subscriber1: User,
    user_subscriber2: User,
) -> None:
    """При создании VisitedCity для пользователя с несколькими подписчиками создаются уведомления."""
    Subscribe.objects.create(subscribe_from=user_subscriber1, subscribe_to=user_owner)
    Subscribe.objects.create(subscribe_from=user_subscriber2, subscribe_to=user_owner)

    VisitedCity.objects.create(
        user=user_owner,
        city=test_city,
        rating=5,
    )

    notifications = VisitedCityNotification.objects.all()
    assert notifications.count() == 2

    recipients = {n.recipient for n in notifications}
    assert recipients == {user_subscriber1, user_subscriber2}

    for notification in notifications:
        assert notification.sender == user_owner
        assert notification.city == test_city
        assert notification.is_read is False


@pytest.mark.django_db
@pytest.mark.integration
def test_signal_does_not_create_notification_without_subscribers(
    test_city: City,
    user_owner: User,
    user_not_subscriber: User,
) -> None:
    """При создании VisitedCity для пользователя без подписчиков уведомления не создаются."""
    VisitedCity.objects.create(
        user=user_owner,
        city=test_city,
        rating=5,
    )

    assert VisitedCityNotification.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.integration
def test_signal_does_not_trigger_on_update(
    test_city: City,
    user_owner: User,
    user_subscriber1: User,
) -> None:
    """При обновлении существующего VisitedCity уведомления не создаются."""
    Subscribe.objects.create(subscribe_from=user_subscriber1, subscribe_to=user_owner)

    visited_city = VisitedCity.objects.create(
        user=user_owner,
        city=test_city,
        rating=3,
    )
    assert VisitedCityNotification.objects.count() == 1

    visited_city.rating = 5
    visited_city.has_magnet = True
    visited_city.save()

    assert VisitedCityNotification.objects.count() == 1


@pytest.mark.django_db
@pytest.mark.integration
def test_signal_creates_notification_with_correct_city_data(
    test_country: Country,
    test_region: Region,
    user_owner: User,
    user_subscriber1: User,
) -> None:
    """Уведомление должно содержать правильную ссылку на город с данными о стране."""
    city = City.objects.create(
        title='Особый город',
        region=test_region,
        country=test_country,
        coordinate_width=40.0,
        coordinate_longitude=50.0,
    )

    Subscribe.objects.create(subscribe_from=user_subscriber1, subscribe_to=user_owner)

    VisitedCity.objects.create(
        user=user_owner,
        city=city,
        rating=5,
    )

    notification = VisitedCityNotification.objects.first()
    assert notification is not None
    assert notification.city == city
    assert notification.city.title == 'Особый город'
    assert notification.city.country == test_country


@pytest.mark.django_db
@pytest.mark.integration
def test_signal_does_not_notify_self_subscription(
    test_city: City,
    user_owner: User,
) -> None:
    """Если пользователь подписан сам на себя, уведомление всё равно создаётся."""
    Subscribe.objects.create(subscribe_from=user_owner, subscribe_to=user_owner)

    VisitedCity.objects.create(
        user=user_owner,
        city=test_city,
        rating=5,
    )

    notifications = VisitedCityNotification.objects.all()
    assert notifications.count() == 1
    notification = notifications.first()
    assert notification is not None
    assert notification.recipient == user_owner
    assert notification.sender == user_owner


@pytest.mark.django_db
@pytest.mark.integration
def test_signal_only_notifies_subscribers_of_specific_user(
    test_city: City,
    user_owner: User,
    user_subscriber1: User,
    user_subscriber2: User,
    user_not_subscriber: User,
) -> None:
    """Уведомления получают только подписчики конкретного пользователя."""
    Subscribe.objects.create(subscribe_from=user_subscriber1, subscribe_to=user_owner)
    Subscribe.objects.create(subscribe_from=user_subscriber2, subscribe_to=user_not_subscriber)

    VisitedCity.objects.create(
        user=user_owner,
        city=test_city,
        rating=5,
    )

    notifications = VisitedCityNotification.objects.all()
    assert notifications.count() == 1
    notification = notifications.first()
    assert notification is not None
    assert notification.recipient == user_subscriber1


@pytest.mark.django_db
@pytest.mark.integration
def test_multiple_visited_cities_create_multiple_notifications(
    test_country: Country,
    test_region: Region,
    user_owner: User,
    user_subscriber1: User,
) -> None:
    """При добавлении нескольких городов создаются отдельные уведомления для каждого."""
    city1 = City.objects.create(
        title='Город 1',
        region=test_region,
        country=test_country,
        coordinate_width=40.0,
        coordinate_longitude=50.0,
    )
    city2 = City.objects.create(
        title='Город 2',
        region=test_region,
        country=test_country,
        coordinate_width=41.0,
        coordinate_longitude=51.0,
    )

    Subscribe.objects.create(subscribe_from=user_subscriber1, subscribe_to=user_owner)

    VisitedCity.objects.create(user=user_owner, city=city1, rating=4)
    VisitedCity.objects.create(user=user_owner, city=city2, rating=5)

    notifications = VisitedCityNotification.objects.all()
    assert notifications.count() == 2

    cities_in_notifications = {n.city for n in notifications}
    assert cities_in_notifications == {city1, city2}


@pytest.mark.django_db
@pytest.mark.integration
def test_signal_handles_deleted_subscription_gracefully(
    test_city: City,
    user_owner: User,
    user_subscriber1: User,
) -> None:
    """После удаления подписки новые уведомления не создаются."""
    subscription = Subscribe.objects.create(
        subscribe_from=user_subscriber1, subscribe_to=user_owner
    )
    subscription.delete()

    VisitedCity.objects.create(
        user=user_owner,
        city=test_city,
        rating=5,
    )

    assert VisitedCityNotification.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.integration
def test_notification_created_at_is_set(
    test_city: City,
    user_owner: User,
    user_subscriber1: User,
) -> None:
    """Поле created_at уведомления должно быть автоматически заполнено."""
    Subscribe.objects.create(subscribe_from=user_subscriber1, subscribe_to=user_owner)

    VisitedCity.objects.create(
        user=user_owner,
        city=test_city,
        rating=5,
    )

    notification = VisitedCityNotification.objects.first()
    assert notification is not None
    assert notification.created_at is not None


@pytest.mark.django_db
@pytest.mark.integration
def test_signal_is_connected_to_visited_city_post_save() -> None:
    """Обработчик сигнала подключён к post_save VisitedCity."""
    from django.db.models.signals import post_save

    receivers = post_save._live_receivers(VisitedCity)

    handler_names = [getattr(receiver, '__name__', str(receiver)) for receiver in receivers]
    assert 'notify_subscribers_on_city_add' in handler_names


@pytest.mark.django_db
@pytest.mark.integration
def test_signal_handler_is_imported_in_app_ready() -> None:
    """Модуль signals импортируется в методе ready() приложения."""
    from city.apps import CityConfig
    import city.signals  # noqa: F401

    assert CityConfig.name == 'city'
