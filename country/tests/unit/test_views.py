"""
Юнит-тесты для views приложения country.
"""

from unittest.mock import Mock, patch

import pytest


@pytest.mark.unit
class TestCountryView:
    """Тесты для функции country."""

    @patch('country.views.render')
    def test_country_view_calls_render(self, mock_render: Mock) -> None:
        """Проверяет что view вызывает render с правильными параметрами."""
        from country.views import country

        request = Mock()
        country(request)

        mock_render.assert_called_once()
        args = mock_render.call_args
        assert args[0][0] == request
        assert args[0][1] == 'country/map.html'

    @patch('country.views.render')
    def test_country_view_context(self, mock_render: Mock) -> None:
        """Проверяет контекст, передаваемый в шаблон."""
        from country.views import country

        request = Mock()
        country(request)

        args = mock_render.call_args
        context = args[1]['context']
        assert 'page_title' in context
        assert 'page_description' in context
        assert context['page_title'] == 'Карта стран мира'
        assert context['page_description'] == 'Карта стран мира'

