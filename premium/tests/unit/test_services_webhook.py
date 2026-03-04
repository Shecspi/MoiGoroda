"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest

from premium.models import PremiumPayment
from premium.services.webhook import WebhookService
from premium.tests.conftest import make_webhook_payload


@pytest.mark.unit
@pytest.mark.django_db
class TestWebhookService:
    """Тесты WebhookService."""

    def test_process_invalid_payload(self) -> None:
        """Невалидный payload возвращает invalid_payload."""
        service = WebhookService()
        result = service.process({'invalid': 'data'})
        assert result.status == 'invalid_payload'

    def test_process_payment_not_found(
        self,
    ) -> None:
        payload = make_webhook_payload(
            payment_id='nonexistent-yookassa-id',
            status='succeeded',
        )
        service = WebhookService()
        result = service.process(payload)
        assert result.status == 'payment_not_found'
        assert result.payment_id == 'nonexistent-yookassa-id'

    def test_process_ok_succeeded_activates_subscription(
        self,
        premium_payment: PremiumPayment,
    ) -> None:
        payload = make_webhook_payload(
            payment_id=premium_payment.yookassa_payment_id,
            status='succeeded',
            event='payment.succeeded',
        )
        service = WebhookService()
        result = service.process(payload)
        assert result.status == 'ok'
        assert result.new_status == 'succeeded'

        premium_payment.refresh_from_db()
        assert premium_payment.status == PremiumPayment.Status.SUCCEEDED

        assert premium_payment.subscription is not None
        premium_payment.subscription.refresh_from_db()
        assert premium_payment.subscription.status == 'active'

    def test_process_ok_canceled(
        self,
        premium_payment: PremiumPayment,
    ) -> None:
        payload = make_webhook_payload(
            payment_id=premium_payment.yookassa_payment_id,
            status='canceled',
            event='payment.canceled',
        )
        service = WebhookService()
        result = service.process(payload)
        assert result.status == 'ok'
        assert result.new_status == 'canceled'

        premium_payment.refresh_from_db()
        assert premium_payment.status == PremiumPayment.Status.CANCELED

    def test_process_transition_denied_succeeded_to_waiting(
        self,
        premium_payment: PremiumPayment,
    ) -> None:
        premium_payment.status = PremiumPayment.Status.SUCCEEDED
        premium_payment.save()

        payload = make_webhook_payload(
            payment_id=premium_payment.yookassa_payment_id,
            status='waiting_for_capture',
            event='payment.waiting_for_capture',
        )
        service = WebhookService()
        result = service.process(payload)
        assert result.status == 'transition_denied'
        assert result.current_status == 'succeeded'
        assert result.new_status == 'waiting_for_capture'

    def test_process_ignored_event(
        self,
    ) -> None:
        payload = {
            'type': 'notification',
            'event': 'refund.succeeded',
            'object': {'id': 'ref-123', 'status': 'succeeded'},
        }
        service = WebhookService()
        result = service.process(payload)
        assert result.status == 'ignored'
