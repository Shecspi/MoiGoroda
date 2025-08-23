import pytest
from city.signals import notify_subscribers_on_city_add


@pytest.fixture
def mock_instance(mocker):
    """Фейковый VisitedCity instance с user и pk"""
    user = mocker.Mock()
    instance = mocker.Mock()
    instance.user = user
    instance.pk = 123
    return instance


class TestNotifySubscribersOnCityAdd:
    def test_not_created_does_nothing(self, mocker, mock_instance):
        """Если created=False — ничего не делаем"""
        mock_subscribe = mocker.patch(
            "city.signals.Subscribe.objects"
        )
        mock_visitedcity = mocker.patch(
            "city.signals.VisitedCity.objects"
        )
        mock_notification = mocker.patch(
            "city.signals.VisitedCityNotification.objects"
        )

        notify_subscribers_on_city_add(sender=None, instance=mock_instance, created=False)

        mock_subscribe.select_related.assert_not_called()
        mock_visitedcity.select_related.assert_not_called()
        mock_notification.create.assert_not_called()

    def test_created_with_no_subscribers(self, mocker, mock_instance):
        """Если подписчиков нет — уведомления не создаются"""
        mock_subscribe = mocker.patch(
            "city.signals.Subscribe.objects"
        )
        mock_subscribe.select_related.return_value.filter.return_value = []

        mock_city = mocker.Mock()
        mock_visitedcity = mocker.patch(
            "city.signals.VisitedCity.objects"
        )
        mock_visitedcity.select_related.return_value.get.return_value.city = mock_city

        mock_notification = mocker.patch(
            "city.signals.VisitedCityNotification.objects"
        )

        notify_subscribers_on_city_add(sender=None, instance=mock_instance, created=True)

        mock_subscribe.select_related.assert_called_once_with("subscribe_from")
        mock_visitedcity.select_related.assert_called_once_with("city", "city__country")
        mock_notification.create.assert_not_called()

    def test_created_with_subscribers(self, mocker, mock_instance):
        """Если есть подписчики — создаются уведомления для каждого"""
        mock_subscribe = mocker.patch(
            "city.signals.Subscribe.objects"
        )
        subscriber1 = mocker.Mock(subscribe_from="u1")
        subscriber2 = mocker.Mock(subscribe_from="u2")
        mock_subscribe.select_related.return_value.filter.return_value = [
            subscriber1, subscriber2
        ]

        mock_city = mocker.Mock()
        mock_visitedcity = mocker.patch(
            "city.signals.VisitedCity.objects"
        )
        mock_visitedcity.select_related.return_value.get.return_value.city = mock_city

        mock_notification = mocker.patch(
            "city.signals.VisitedCityNotification.objects"
        )

        notify_subscribers_on_city_add(sender=None, instance=mock_instance, created=True)

        assert mock_notification.create.call_count == 2
        mock_notification.create.assert_any_call(
            recipient="u1", sender=mock_instance.user, city=mock_city
        )
        mock_notification.create.assert_any_call(
            recipient="u2", sender=mock_instance.user, city=mock_city
        )

    def test_city_is_fetched_by_instance_pk(self, mocker, mock_instance):
        """Проверяем, что город берется по pk инстанса"""
        mock_subscribe = mocker.patch(
            "city.signals.Subscribe.objects"
        )
        mock_subscribe.select_related.return_value.filter.return_value = []

        mock_qs = mocker.Mock()
        mocker.patch(
            "city.signals.VisitedCity.objects",
            return_value=mock_qs
        )
        mock_select_related = mocker.patch(
            "city.signals.VisitedCity.objects.select_related"
        )
        mock_get = mock_select_related.return_value.get

        notify_subscribers_on_city_add(sender=None, instance=mock_instance, created=True)

        mock_get.assert_called_once_with(pk=mock_instance.pk)
