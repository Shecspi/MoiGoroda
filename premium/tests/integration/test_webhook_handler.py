"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import json

import pytest
from django.conf import LazySettings
from django.test import Client

from premium.models import PremiumPayment
from premium.tests.conftest import make_webhook_payload


@pytest.fixture(autouse=True)
def disable_webhook_ip_verification(settings: LazySettings) -> None:
    """Отключает проверку IP вебхука для тестов."""
    settings.YOOKASSA_WEBHOOK_IP_VERIFICATION = False


@pytest.mark.integration
@pytest.mark.django_db
class TestYookassaWebhookHandler:
    """Тесты обработчика вебхука YooKassa."""

    def test_webhook_returns_200_always(self) -> None:
        """Вебхук всегда возвращает 200, чтобы YooKassa не повторял запрос."""
        client = Client()
        response = client.post(
            '/premium/webhook/yookassa/',
            data=json.dumps({'invalid': 'data'}),
            content_type='application/json',
        )
        assert response.status_code == 200

    def test_webhook_invalid_json_returns_200(self) -> None:
        client = Client()
        response = client.post(
            '/premium/webhook/yookassa/',
            data='not json',
            content_type='application/json',
        )
        assert response.status_code == 200

    def test_webhook_valid_payload_succeeded(
        self,
        premium_payment: PremiumPayment,
    ) -> None:
        payload = make_webhook_payload(
            payment_id=premium_payment.yookassa_payment_id,
            status='succeeded',
            event='payment.succeeded',
        )
        client = Client()
        response = client.post(
            '/premium/webhook/yookassa/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        assert response.status_code == 200

        premium_payment.refresh_from_db()
        assert premium_payment.status == 'succeeded'
