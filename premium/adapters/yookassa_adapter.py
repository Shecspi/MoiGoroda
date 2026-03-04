"""
Адаптер платёжного провайдера YooKassa.
Инкапсулирует работу с API YooKassa.
"""

from __future__ import annotations

import json
import uuid

from django.conf import settings
from yookassa import Configuration, Payment  # type: ignore[import-untyped]
from yookassa.domain.exceptions import ApiError  # type: ignore[import-untyped]

from premium.adapters.payment_provider import CreatePaymentResult


class YooKassaPaymentAdapter:
    """Адаптер для создания платежей в YooKassa."""

    def __init__(
        self,
        shop_id: str | None = None,
        secret_key: str | None = None,
    ) -> None:
        self._shop_id = shop_id or settings.YOOKASSA_SHOP_ID
        self._secret_key = secret_key or settings.YOOKASSA_SECRET_KEY

    def create_payment(
        self,
        amount_value: str,
        currency: str,
        description: str,
        return_url: str,
        idempotency_key: str,
    ) -> CreatePaymentResult:
        """
        Создаёт платёж в YooKassa.

        Raises:
            ApiError: при ошибке API YooKassa.
        """
        Configuration.account_id = self._shop_id
        Configuration.secret_key = self._secret_key

        payment = Payment.create(
            {
                'amount': {
                    'value': amount_value,
                    'currency': currency,
                },
                'confirmation': {
                    'type': 'redirect',
                    'return_url': return_url,
                },
                'capture': True,
                'description': description,
            },
            uuid.UUID(idempotency_key) if isinstance(idempotency_key, str) else idempotency_key,
        )

        try:
            response_data = json.loads(payment.json())
        except (TypeError, ValueError):
            response_data = {}

        confirmation_url = ''
        if payment.confirmation:
            confirmation_url = getattr(
                payment.confirmation,
                'confirmation_url',
                '',
            ) or ''

        return CreatePaymentResult(
            payment_id=payment.id,
            status=payment.status,
            confirmation_url=confirmation_url,
            raw_response=response_data,
        )
