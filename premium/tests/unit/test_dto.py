"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest

from premium.dto import CheckoutResult, SubscriptionPageData, WebhookProcessResult


@pytest.mark.unit
class TestCheckoutResult:
    """Тесты DTO CheckoutResult."""

    def test_success_result(self) -> None:
        result = CheckoutResult(
            success=True,
            redirect_url='https://yookassa.ru/pay',
            payment_id='uuid-123',
            yookassa_payment_id='yk-123',
            yookassa_status='pending',
            raw_response={'id': 'yk-123'},
        )
        assert result.success is True
        assert result.redirect_url == 'https://yookassa.ru/pay'
        assert result.payment_id == 'uuid-123'
        assert result.yookassa_payment_id == 'yk-123'
        assert result.yookassa_status == 'pending'
        assert result.raw_response == {'id': 'yk-123'}

    def test_failure_result(self) -> None:
        result = CheckoutResult(
            success=False,
            redirect_url='https://site.com/promo',
        )
        assert result.success is False
        assert result.payment_id is None
        assert result.yookassa_payment_id == ''


@pytest.mark.unit
class TestSubscriptionPageData:
    """Тесты DTO SubscriptionPageData."""

    def test_creation(self) -> None:
        data = SubscriptionPageData(
            payments=[],
            active_subscription=None,
            paused_subscriptions=[],
            payment_result='succeeded',
        )
        assert data.payments == []
        assert data.active_subscription is None
        assert data.paused_subscriptions == []
        assert data.payment_result == 'succeeded'


@pytest.mark.unit
class TestWebhookProcessResult:
    """Тесты DTO WebhookProcessResult."""

    def test_ok_result(self) -> None:
        result = WebhookProcessResult(
            status='ok',
            payment_id='yk-123',
            new_status='succeeded',
        )
        assert result.status == 'ok'
        assert result.payment_id == 'yk-123'
        assert result.new_status == 'succeeded'

    def test_invalid_payload_result(self) -> None:
        error = ValueError('Invalid type')
        result = WebhookProcessResult(
            status='invalid_payload',
            data={'type': 'unknown'},
            error=error,
        )
        assert result.status == 'invalid_payload'
        assert result.data == {'type': 'unknown'}
        assert result.error is error
