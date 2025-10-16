"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from unittest.mock import Mock, patch

from django.test import RequestFactory

from dashboard.views import Dashboard


# ===== Unit тесты для Dashboard View =====


@pytest.mark.unit
def test_dashboard_view_has_correct_template() -> None:
    """Тест что Dashboard использует правильный шаблон"""
    assert Dashboard.template_name == 'dashboard/dashboard.html'


@pytest.mark.unit
def test_dashboard_view_requires_login() -> None:
    """Тест что Dashboard требует авторизации"""
    from django.contrib.auth.mixins import LoginRequiredMixin

    assert issubclass(Dashboard, LoginRequiredMixin)


@pytest.mark.unit
def test_dashboard_view_uses_template_view() -> None:
    """Тест что Dashboard наследуется от TemplateView"""
    from django.views.generic import TemplateView

    assert issubclass(Dashboard, TemplateView)


@pytest.mark.unit
def test_dashboard_dispatch_redirects_non_superuser() -> None:
    """Тест что dispatch редиректит не-суперюзера"""
    rf = RequestFactory()
    request = rf.get('/dashboard/')
    request.user = Mock(is_superuser=False)

    view = Dashboard()
    view.request = request

    with patch('dashboard.views.redirect') as mock_redirect:
        view.dispatch(request)
        mock_redirect.assert_called_once_with('main_page')


@pytest.mark.unit
def test_dashboard_dispatch_allows_superuser() -> None:
    """Тест что dispatch пропускает суперюзера"""
    rf = RequestFactory()
    request = rf.get('/dashboard/')
    request.user = Mock(is_superuser=True)

    view = Dashboard()
    view.request = request

    with patch.object(Dashboard, 'get_context_data', return_value={}):
        with patch('django.views.generic.TemplateView.dispatch') as mock_super_dispatch:
            mock_super_dispatch.return_value = Mock()
            view.dispatch(request)
            mock_super_dispatch.assert_called_once()


@pytest.mark.unit
def test_dashboard_context_data_keys() -> None:
    """Тест что get_context_data возвращает правильные ключи"""
    expected_keys = {
        'qty_users',
        'qty_registrations_yesteday',
        'qty_registrations_week',
        'qty_registrations_month',
        'registrations_by_day',
        'qty_visited_cities',
        'average_cities',
        'qty_visited_cities_by_user',
        'qty_user_without_visited_cities',
        'page_title',
        'page_description',
    }

    rf = RequestFactory()
    request = rf.get('/dashboard/')
    request.user = Mock(is_superuser=True)

    view = Dashboard()
    view.request = request

    with patch('dashboard.views.User.objects') as mock_user_objects:
        with patch('dashboard.views.VisitedCity.objects') as mock_vc_objects:
            mock_user_objects.count.return_value = 10
            mock_user_objects.filter.return_value.count.return_value = 5
            mock_user_objects.annotate.return_value.filter.return_value.count.return_value = 3
            mock_vc_objects.count.return_value = 100
            mock_user_objects.annotate.return_value.values.return_value.exclude.return_value.order_by.return_value = []

            context = view.get_context_data()

            for key in expected_keys:
                assert key in context


@pytest.mark.unit
def test_dashboard_page_title_is_dashboard() -> None:
    """Тест что page_title равен 'Dashboard'"""
    rf = RequestFactory()
    request = rf.get('/dashboard/')
    request.user = Mock(is_superuser=True)

    view = Dashboard()
    view.request = request

    with patch('dashboard.views.User.objects') as mock_user_objects:
        with patch('dashboard.views.VisitedCity.objects') as mock_vc_objects:
            mock_user_objects.count.return_value = 10
            mock_user_objects.filter.return_value.count.return_value = 5
            mock_user_objects.annotate.return_value.filter.return_value.count.return_value = 3
            mock_vc_objects.count.return_value = 100
            mock_user_objects.annotate.return_value.values.return_value.exclude.return_value.order_by.return_value = []

            context = view.get_context_data()

            assert context['page_title'] == 'Dashboard'


@pytest.mark.unit
def test_dashboard_average_cities_calculation() -> None:
    """Тест расчета среднего количества городов"""
    rf = RequestFactory()
    request = rf.get('/dashboard/')
    request.user = Mock(is_superuser=True)

    view = Dashboard()
    view.request = request

    with patch('dashboard.views.User.objects') as mock_user_objects:
        with patch('dashboard.views.VisitedCity.objects') as mock_vc_objects:
            mock_user_objects.count.return_value = 10
            mock_user_objects.filter.return_value.count.return_value = 5
            mock_user_objects.annotate.return_value.filter.return_value.count.return_value = 3
            mock_vc_objects.count.return_value = 100
            mock_user_objects.annotate.return_value.values.return_value.exclude.return_value.order_by.return_value = []

            context = view.get_context_data()

            # 100 городов / 10 пользователей = 10
            assert context['average_cities'] == 10
