"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from unittest.mock import patch

import pytest
from django.test import RequestFactory

from premium.webhook.logging import (
    log_invalid_json,
    log_invalid_payload,
    log_payment_not_found,
    log_status_updated,
    log_transition_denied,
    log_yookassa_create_response,
)


@pytest.mark.unit
class TestWebhookLogging:
    """Тесты функций логирования вебхука."""

    @pytest.fixture
    def request_obj(self) -> RequestFactory:
        return RequestFactory()

    def test_log_invalid_json(self, request_obj: RequestFactory) -> None:
        request = request_obj.post(
            '/webhook/',
            data=b'not valid json',
            content_type='application/json',
        )
        with patch('premium.webhook.logging.logger') as mock_logger:
            log_invalid_json(request, ValueError('Expecting value'))
            mock_logger.warning.assert_called_once()
            assert 'Невалидный JSON' in mock_logger.warning.call_args[0][0]

    def test_log_invalid_payload(self, request_obj: RequestFactory) -> None:
        request = request_obj.post('/webhook/', data={})
        with patch('premium.webhook.logging.logger') as mock_logger:
            log_invalid_payload(
                request,
                {'type': 'x', 'event': 'y', 'object': {'id': 'z'}},
                ValueError('Invalid'),
            )
            mock_logger.warning.assert_called_once()
            assert 'Невалидный payload' in mock_logger.warning.call_args[0][0]

    def test_log_payment_not_found(self, request_obj: RequestFactory) -> None:
        request = request_obj.post('/webhook/')
        with patch('premium.webhook.logging.logger') as mock_logger:
            log_payment_not_found(request, 'yk-123')
            mock_logger.info.assert_called_once()
            assert 'Платёж не найден' in mock_logger.info.call_args[0][0]
            assert 'yk-123' in str(mock_logger.info.call_args)

    def test_log_transition_denied(self, request_obj: RequestFactory) -> None:
        request = request_obj.post('/webhook/')
        with patch('premium.webhook.logging.logger') as mock_logger:
            log_transition_denied(
                request,
                payment_id='yk-123',
                current_status='succeeded',
                new_status='waiting_for_capture',
            )
            mock_logger.info.assert_called_once()
            assert 'Переход статуса отклонён' in mock_logger.info.call_args[0][0]

    def test_log_status_updated(self, request_obj: RequestFactory) -> None:
        request = request_obj.post('/webhook/')
        with patch('premium.webhook.logging.logger') as mock_logger:
            log_status_updated(request, 'yk-123', 'succeeded')
            mock_logger.info.assert_called_once()
            assert 'Статус обновлён' in mock_logger.info.call_args[0][0]

    def test_log_yookassa_create_response_authenticated(
        self,
        request_obj: RequestFactory,
    ) -> None:
        """Тест логирования для аутентифицированного пользователя (мок user)."""
        request = request_obj.post('/checkout/')
        request.user = type('User', (), {'username': 'testuser', 'is_authenticated': True})()
        with patch('premium.webhook.logging.logger') as mock_logger:
            log_yookassa_create_response(request, 'yk-123', 'pending')
            mock_logger.info.assert_called_once()
            assert 'YooKassa создан платёж' in mock_logger.info.call_args[0][0]

    def test_log_yookassa_create_response_anonymous(
        self,
        request_obj: RequestFactory,
    ) -> None:
        from django.contrib.auth.models import AnonymousUser

        request = request_obj.post('/checkout/')
        request.user = AnonymousUser()
        with patch('premium.webhook.logging.logger') as mock_logger:
            log_yookassa_create_response(request, 'yk-123', 'pending')
            mock_logger.info.assert_called_once()
