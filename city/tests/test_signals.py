from typing import Any
import pytest

from city.signals import notify_subscribers_on_city_add
from city.models import VisitedCity


@pytest.fixture
def mock_instance(mocker: Any) -> Any:
    """Фейковый VisitedCity instance с user и pk"""
    user = mocker.Mock()
    instance = mocker.Mock()
    instance.user = user
    instance.pk = 123
    return instance


class TestNotifySubscribersOnCityAdd:
    def test_not_created_does_nothing(self, mocker: Any, mock_instance: Any) -> None:
        """Если created=False — ничего не делаем"""
        mock_subscribe = mocker.patch('city.signals.Subscribe.objects')
        mock_visitedcity = mocker.patch('city.signals.VisitedCity.objects')
        mock_notification = mocker.patch('city.signals.VisitedCityNotification.objects')

        notify_subscribers_on_city_add(
            sender=type(mock_instance), instance=mock_instance, created=False
        )

        mock_subscribe.select_related.assert_not_called()
        mock_visitedcity.select_related.assert_not_called()
        mock_notification.create.assert_not_called()

    def test_created_with_no_subscribers(self, mocker: Any, mock_instance: Any) -> None:
        """Если подписчиков нет — уведомления не создаются"""
        mock_subscribe = mocker.patch('city.signals.Subscribe.objects')
        mock_subscribe.select_related.return_value.filter.return_value = []

        mock_city = mocker.Mock()
        mock_visitedcity = mocker.patch('city.signals.VisitedCity.objects')
        mock_visitedcity.select_related.return_value.get.return_value.city = mock_city

        mock_notification = mocker.patch('city.signals.VisitedCityNotification.objects')

        notify_subscribers_on_city_add(sender=VisitedCity, instance=mock_instance, created=True)

        mock_subscribe.select_related.assert_called_once_with('subscribe_from')
        mock_visitedcity.select_related.assert_called_once_with('city', 'city__country')
        mock_notification.create.assert_not_called()

    def test_created_with_subscribers(self, mocker: Any, mock_instance: Any) -> None:
        """Если есть подписчики — создаются уведомления для каждого"""
        mock_subscribe = mocker.patch('city.signals.Subscribe.objects')
        subscriber1 = mocker.Mock(subscribe_from='u1')
        subscriber2 = mocker.Mock(subscribe_from='u2')
        mock_subscribe.select_related.return_value.filter.return_value = [subscriber1, subscriber2]

        mock_city = mocker.Mock()
        mock_visitedcity = mocker.patch('city.signals.VisitedCity.objects')
        mock_visitedcity.select_related.return_value.get.return_value.city = mock_city

        mock_notification = mocker.patch('city.signals.VisitedCityNotification.objects')

        notify_subscribers_on_city_add(sender=VisitedCity, instance=mock_instance, created=True)

        assert mock_notification.create.call_count == 2
        mock_notification.create.assert_any_call(
            recipient='u1', sender=mock_instance.user, city=mock_city
        )
        mock_notification.create.assert_any_call(
            recipient='u2', sender=mock_instance.user, city=mock_city
        )

    def test_city_is_fetched_by_instance_pk(self, mocker: Any, mock_instance: Any) -> None:
        """Проверяем, что город берется по pk инстанса"""
        mock_subscribe = mocker.patch('city.signals.Subscribe.objects')
        mock_subscribe.select_related.return_value.filter.return_value = []

        mock_qs = mocker.Mock()
        mocker.patch('city.signals.VisitedCity.objects', return_value=mock_qs)
        mock_select_related = mocker.patch('city.signals.VisitedCity.objects.select_related')
        mock_get = mock_select_related.return_value.get

        notify_subscribers_on_city_add(sender=VisitedCity, instance=mock_instance, created=True)

        mock_get.assert_called_once_with(pk=mock_instance.pk)

    def test_created_with_none_user(self, mocker: Any) -> None:
        """Проверяем поведение при отсутствии пользователя"""
        instance = mocker.Mock()
        instance.user = None
        instance.pk = 123

        mock_subscribe = mocker.patch('city.signals.Subscribe.objects')
        mock_subscribe.select_related.return_value.filter.return_value = []

        mock_visitedcity = mocker.patch('city.signals.VisitedCity.objects')
        mock_visitedcity.select_related.return_value.get.return_value.city = mocker.Mock()

        # Функция должна выполниться без ошибок, но с None в качестве user
        notify_subscribers_on_city_add(sender=VisitedCity, instance=instance, created=True)

        # Проверяем, что функция выполнилась
        mock_subscribe.select_related.assert_called_once_with('subscribe_from')

    def test_created_with_none_pk(self, mocker: Any) -> None:
        """Проверяем поведение при отсутствии pk"""
        user = mocker.Mock()
        instance = mocker.Mock()
        instance.user = user
        instance.pk = None

        mock_subscribe = mocker.patch('city.signals.Subscribe.objects')
        mock_subscribe.select_related.return_value.filter.return_value = []

        mock_visitedcity = mocker.patch('city.signals.VisitedCity.objects')
        mock_visitedcity.select_related.return_value.get.return_value.city = mocker.Mock()

        # Функция должна выполниться без ошибок, передав None в качестве pk
        notify_subscribers_on_city_add(sender=VisitedCity, instance=instance, created=True)

        # Проверяем, что функция выполнилась
        mock_subscribe.select_related.assert_called_once_with('subscribe_from')

    def test_created_with_invalid_pk(self, mocker: Any) -> None:
        """Проверяем поведение при несуществующем pk"""
        user = mocker.Mock()
        instance = mocker.Mock()
        instance.user = user
        instance.pk = 999999  # Несуществующий ID

        mock_subscribe = mocker.patch('city.signals.Subscribe.objects')
        mock_subscribe.select_related.return_value.filter.return_value = []

        mock_visitedcity = mocker.patch('city.signals.VisitedCity.objects')
        mock_visitedcity.select_related.return_value.get.side_effect = Exception('DoesNotExist')

        # Должно вызвать исключение при попытке получить несуществующий объект
        with pytest.raises(Exception):
            notify_subscribers_on_city_add(sender=VisitedCity, instance=instance, created=True)

    def test_created_with_none_city(self, mocker: Any) -> None:
        """Проверяем поведение при отсутствии города"""
        user = mocker.Mock()
        instance = mocker.Mock()
        instance.user = user
        instance.pk = 123

        mock_subscribe = mocker.patch('city.signals.Subscribe.objects')
        mock_subscribe.select_related.return_value.filter.return_value = []

        mock_visitedcity = mocker.patch('city.signals.VisitedCity.objects')
        mock_visitedcity.select_related.return_value.get.return_value.city = None

        notify_subscribers_on_city_add(sender=VisitedCity, instance=instance, created=True)

        # Должно выполниться без ошибок, но без создания уведомлений
        # (проверяем, что функция выполнилась без исключений)

    def test_created_with_database_error_on_subscribers(
        self, mocker: Any, mock_instance: Any
    ) -> None:
        """Проверяем поведение при ошибке базы данных при получении подписчиков"""
        mock_subscribe = mocker.patch('city.signals.Subscribe.objects')
        mock_subscribe.select_related.side_effect = Exception('Database error')

        # Должно вызвать исключение при ошибке базы данных
        with pytest.raises(Exception):
            notify_subscribers_on_city_add(sender=VisitedCity, instance=mock_instance, created=True)

    def test_created_with_database_error_on_notification_creation(
        self, mocker: Any, mock_instance: Any
    ) -> None:
        """Проверяем поведение при ошибке создания уведомления"""
        mock_subscribe = mocker.patch('city.signals.Subscribe.objects')
        subscriber = mocker.Mock(subscribe_from='u1')
        mock_subscribe.select_related.return_value.filter.return_value = [subscriber]

        mock_city = mocker.Mock()
        mock_visitedcity = mocker.patch('city.signals.VisitedCity.objects')
        mock_visitedcity.select_related.return_value.get.return_value.city = mock_city

        mock_notification = mocker.patch('city.signals.VisitedCityNotification.objects')
        mock_notification.create.side_effect = Exception('Database error')

        # Должно вызвать исключение при ошибке создания уведомления
        with pytest.raises(Exception):
            notify_subscribers_on_city_add(sender=VisitedCity, instance=mock_instance, created=True)

    def test_created_with_multiple_subscribers_same_user(
        self, mocker: Any, mock_instance: Any
    ) -> None:
        """Проверяем поведение с несколькими подписчиками от одного пользователя"""
        mock_subscribe = mocker.patch('city.signals.Subscribe.objects')
        subscriber1 = mocker.Mock(subscribe_from='u1')
        subscriber2 = mocker.Mock(subscribe_from='u1')  # Тот же пользователь
        subscriber3 = mocker.Mock(subscribe_from='u2')
        mock_subscribe.select_related.return_value.filter.return_value = [
            subscriber1,
            subscriber2,
            subscriber3,
        ]

        mock_city = mocker.Mock()
        mock_visitedcity = mocker.patch('city.signals.VisitedCity.objects')
        mock_visitedcity.select_related.return_value.get.return_value.city = mock_city

        mock_notification = mocker.patch('city.signals.VisitedCityNotification.objects')

        notify_subscribers_on_city_add(sender=VisitedCity, instance=mock_instance, created=True)

        # Должно создать уведомления для всех подписчиков, даже дублирующихся
        assert mock_notification.create.call_count == 3
        mock_notification.create.assert_any_call(
            recipient='u1', sender=mock_instance.user, city=mock_city
        )
        mock_notification.create.assert_any_call(
            recipient='u2', sender=mock_instance.user, city=mock_city
        )

    def test_created_with_empty_subscriber_list(self, mocker: Any, mock_instance: Any) -> None:
        """Проверяем поведение с пустым списком подписчиков"""
        mock_subscribe = mocker.patch('city.signals.Subscribe.objects')
        mock_subscribe.select_related.return_value.filter.return_value = []

        mock_city = mocker.Mock()
        mock_visitedcity = mocker.patch('city.signals.VisitedCity.objects')
        mock_visitedcity.select_related.return_value.get.return_value.city = mock_city

        mock_notification = mocker.patch('city.signals.VisitedCityNotification.objects')

        notify_subscribers_on_city_add(sender=VisitedCity, instance=mock_instance, created=True)

        # Должно выполниться без ошибок, но без создания уведомлений
        mock_notification.create.assert_not_called()

    def test_created_with_none_subscriber_from(self, mocker: Any, mock_instance: Any) -> None:
        """Проверяем поведение с подписчиком, у которого subscribe_from = None"""
        mock_subscribe = mocker.patch('city.signals.Subscribe.objects')
        subscriber = mocker.Mock(subscribe_from=None)
        mock_subscribe.select_related.return_value.filter.return_value = [subscriber]

        mock_city = mocker.Mock()
        mock_visitedcity = mocker.patch('city.signals.VisitedCity.objects')
        mock_visitedcity.select_related.return_value.get.return_value.city = mock_city

        mock_notification = mocker.patch('city.signals.VisitedCityNotification.objects')

        notify_subscribers_on_city_add(sender=VisitedCity, instance=mock_instance, created=True)

        # Должно создать уведомление с recipient=None
        mock_notification.create.assert_called_once_with(
            recipient=None, sender=mock_instance.user, city=mock_city
        )

    def test_created_verifies_sender_parameter(self, mocker: Any, mock_instance: Any) -> None:
        """Проверяем, что функция корректно обрабатывает параметр sender"""
        mock_subscribe = mocker.patch('city.signals.Subscribe.objects')
        mock_subscribe.select_related.return_value.filter.return_value = []

        mock_visitedcity = mocker.patch('city.signals.VisitedCity.objects')
        mock_visitedcity.select_related.return_value.get.return_value.city = mocker.Mock()

        # Передаем sender, но функция должна его игнорировать
        notify_subscribers_on_city_add(sender=VisitedCity, instance=mock_instance, created=True)

        # Проверяем, что функция выполнилась без ошибок
        mock_subscribe.select_related.assert_called_once_with('subscribe_from')

    def test_created_verifies_kwargs_parameter(self, mocker: Any, mock_instance: Any) -> None:
        """Проверяем, что функция корректно обрабатывает дополнительные kwargs"""
        mock_subscribe = mocker.patch('city.signals.Subscribe.objects')
        mock_subscribe.select_related.return_value.filter.return_value = []

        mock_visitedcity = mocker.patch('city.signals.VisitedCity.objects')
        mock_visitedcity.select_related.return_value.get.return_value.city = mocker.Mock()

        # Передаем дополнительные kwargs
        notify_subscribers_on_city_add(
            sender=VisitedCity,
            instance=mock_instance,
            created=True,
            extra_param='test',
            another_param=123,
        )

        # Проверяем, что функция выполнилась без ошибок
        mock_subscribe.select_related.assert_called_once_with('subscribe_from')

    def test_created_with_large_number_of_subscribers(
        self, mocker: Any, mock_instance: Any
    ) -> None:
        """Проверяем поведение с большим количеством подписчиков"""
        mock_subscribe = mocker.patch('city.signals.Subscribe.objects')

        # Создаем 100 подписчиков
        subscribers: list[Any] = []
        for i in range(100):
            subscriber = mocker.Mock(subscribe_from=f'user_{i}')
            subscribers.append(subscriber)

        mock_subscribe.select_related.return_value.filter.return_value = subscribers

        mock_city = mocker.Mock()
        mock_visitedcity = mocker.patch('city.signals.VisitedCity.objects')
        mock_visitedcity.select_related.return_value.get.return_value.city = mock_city

        mock_notification = mocker.patch('city.signals.VisitedCityNotification.objects')

        notify_subscribers_on_city_add(sender=VisitedCity, instance=mock_instance, created=True)

        # Должно создать уведомления для всех 100 подписчиков
        assert mock_notification.create.call_count == 100

    def test_created_verifies_query_optimization(self, mocker: Any, mock_instance: Any) -> None:
        """Проверяем, что используются правильные select_related для оптимизации запросов"""
        mock_subscribe = mocker.patch('city.signals.Subscribe.objects')
        mock_subscribe.select_related.return_value.filter.return_value = []

        mock_visitedcity = mocker.patch('city.signals.VisitedCity.objects')

        notify_subscribers_on_city_add(sender=VisitedCity, instance=mock_instance, created=True)

        # Проверяем, что используются правильные select_related
        mock_subscribe.select_related.assert_called_once_with('subscribe_from')
        mock_visitedcity.select_related.assert_called_once_with('city', 'city__country')
