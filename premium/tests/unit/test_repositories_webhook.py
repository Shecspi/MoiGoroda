"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest

from premium.models import PremiumPayment
from premium.repositories.webhook import WebhookRepository


@pytest.mark.unit
@pytest.mark.django_db
class TestWebhookRepository:
    """Тесты WebhookRepository."""

    def test_get_payment_by_yookassa_id(
        self,
        premium_payment: PremiumPayment,
    ) -> None:
        repo = WebhookRepository()
        payment = repo.get_payment_by_yookassa_id(premium_payment.yookassa_payment_id)
        assert payment is not None
        assert payment.pk == premium_payment.pk

    def test_get_payment_by_yookassa_id_none(self) -> None:
        repo = WebhookRepository()
        assert repo.get_payment_by_yookassa_id('nonexistent-id') is None

    def test_create_webhook_log(
        self,
        premium_payment: PremiumPayment,
    ) -> None:
        repo = WebhookRepository()
        log = repo.create_webhook_log(
            payment=premium_payment,
            status='succeeded',
            raw_payload={'event': 'payment.succeeded', 'object': {'id': '123'}},
        )
        assert log.payment == premium_payment
        assert log.status == 'succeeded'
        assert log.raw_payload['event'] == 'payment.succeeded'
