"""
Тесты проверки IP для вебхука YooKassa.
"""

from unittest.mock import patch

import pytest
from django.test import RequestFactory, override_settings


@pytest.mark.unit
class TestYookassaWebhookIPSecurity:
    """Тесты is_yookassa_webhook_ip_allowed."""

    @pytest.fixture
    def request_factory(self) -> RequestFactory:
        return RequestFactory()

    def test_returns_true_when_verification_disabled(
        self,
        request_factory: RequestFactory,
    ) -> None:
        with override_settings(YOOKASSA_WEBHOOK_IP_VERIFICATION=False):
            from premium.webhook.security import is_yookassa_webhook_ip_allowed

            request = request_factory.post(
                '/webhook/',
                REMOTE_ADDR='1.2.3.4',
            )
            assert is_yookassa_webhook_ip_allowed(request) is True

    def test_returns_true_for_yookassa_ip(
        self,
        request_factory: RequestFactory,
    ) -> None:
        with override_settings(YOOKASSA_WEBHOOK_IP_VERIFICATION=True):
            from premium.webhook.security import is_yookassa_webhook_ip_allowed

            request = request_factory.post(
                '/webhook/',
                REMOTE_ADDR='185.71.76.1',
            )
            assert is_yookassa_webhook_ip_allowed(request) is True

    def test_returns_false_for_unknown_ip(
        self,
        request_factory: RequestFactory,
    ) -> None:
        with override_settings(YOOKASSA_WEBHOOK_IP_VERIFICATION=True):
            from premium.webhook.security import is_yookassa_webhook_ip_allowed

            request = request_factory.post(
                '/webhook/',
                REMOTE_ADDR='192.168.1.1',
            )
            assert is_yookassa_webhook_ip_allowed(request) is False

    def test_uses_x_forwarded_for_when_present(
        self,
        request_factory: RequestFactory,
    ) -> None:
        with override_settings(YOOKASSA_WEBHOOK_IP_VERIFICATION=True):
            from premium.webhook.security import is_yookassa_webhook_ip_allowed

            request = request_factory.post(
                '/webhook/',
                HTTP_X_FORWARDED_FOR='185.71.77.5, 10.0.0.1',
                REMOTE_ADDR='10.0.0.1',
            )
            assert is_yookassa_webhook_ip_allowed(request) is True
