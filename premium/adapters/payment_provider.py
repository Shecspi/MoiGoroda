"""
Интерфейс платёжного провайдера.
Позволяет подменять реализацию (YooKassa, Stripe и т.д.) без изменения сервиса.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class CreatePaymentResult:
    """Результат создания платежа у провайдера."""

    payment_id: str
    status: str
    confirmation_url: str
    raw_response: dict[str, Any]


class PaymentProvider(Protocol):
    """Протокол платёжного провайдера."""

    def create_payment(
        self,
        amount_value: str,
        currency: str,
        description: str,
        return_url: str,
        idempotency_key: str,
    ) -> CreatePaymentResult:
        """Создаёт платёж и возвращает данные для редиректа пользователя."""
        ...
