"""
DTO (Data Transfer Objects) для premium-приложения.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from premium.models import PremiumSubscription


@dataclass
class SubscriptionPageData:
    """Данные для страницы «Моя подписка»."""

    payments: list
    active_subscription: PremiumSubscription | None
    paused_subscriptions: list[tuple]
    payment_result: str | None


@dataclass
class WebhookProcessResult:
    """Результат обработки вебхука YooKassa."""

    status: str  # 'ok' | 'invalid_payload' | 'payment_not_found' | 'transition_denied' | 'ignored'
    payment_id: str = ''
    current_status: str = ''
    new_status: str = ''
    data: dict | None = None  # для log_invalid_payload
    error: BaseException | None = None  # для log_invalid_payload


@dataclass
class CheckoutResult:
    """Результат операции checkout."""

    success: bool
    redirect_url: str
    payment_id: str | None = None
    """ID PremiumPayment для сохранения в сессию (при успехе)."""
    yookassa_payment_id: str = ''
    yookassa_status: str = ''
    raw_response: dict | None = None
    """Данные для логирования ответа провайдера."""
