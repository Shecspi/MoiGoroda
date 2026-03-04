"""Адаптеры внешних сервисов (платёжные провайдеры и т.д.)."""

from premium.adapters.payment_provider import CreatePaymentResult, PaymentProvider
from premium.adapters.yookassa_adapter import YooKassaPaymentAdapter

__all__ = [
    'CreatePaymentResult',
    'PaymentProvider',
    'YooKassaPaymentAdapter',
]
