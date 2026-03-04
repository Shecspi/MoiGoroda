"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from unittest.mock import MagicMock, patch

import pytest

from premium.adapters.payment_provider import CreatePaymentResult
from premium.adapters.yookassa_adapter import YooKassaPaymentAdapter


@pytest.mark.unit
class TestCreatePaymentResult:
    """Тесты CreatePaymentResult."""

    def test_dataclass_fields(self) -> None:
        result = CreatePaymentResult(
            payment_id='id',
            status='pending',
            confirmation_url='https://pay.ru',
            raw_response={'id': 'id'},
        )
        assert result.payment_id == 'id'
        assert result.status == 'pending'
        assert result.confirmation_url == 'https://pay.ru'
        assert result.raw_response == {'id': 'id'}


@pytest.mark.unit
class TestYooKassaPaymentAdapter:
    """Тесты YooKassaPaymentAdapter."""

    def test_init_uses_settings_by_default(self) -> None:
        with patch('premium.adapters.yookassa_adapter.settings') as mock_settings:
            mock_settings.YOOKASSA_SHOP_ID = 'shop123'
            mock_settings.YOOKASSA_SECRET_KEY = 'secret456'
            adapter = YooKassaPaymentAdapter()
            assert adapter._shop_id == 'shop123'
            assert adapter._secret_key == 'secret456'

    def test_init_uses_provided_credentials(self) -> None:
        adapter = YooKassaPaymentAdapter(shop_id='custom_shop', secret_key='custom_secret')
        assert adapter._shop_id == 'custom_shop'
        assert adapter._secret_key == 'custom_secret'

    @patch('premium.adapters.yookassa_adapter.Payment')
    def test_create_payment_success(
        self,
        mock_payment_class: MagicMock,
    ) -> None:
        mock_payment = MagicMock()
        mock_payment.id = 'yk-payment-123'
        mock_payment.status = 'pending'
        mock_payment.confirmation = MagicMock()
        mock_payment.confirmation.confirmation_url = 'https://yookassa.ru/confirm'
        mock_payment.json.return_value = '{"id":"yk-payment-123","status":"pending"}'
        mock_payment_class.create.return_value = mock_payment

        adapter = YooKassaPaymentAdapter(shop_id='shop', secret_key='secret')
        result = adapter.create_payment(
            amount_value='299.00',
            currency='RUB',
            description='Test',
            return_url='https://site.com/return',
            idempotency_key='12345678-1234-5678-1234-567812345678',
        )

        assert result.payment_id == 'yk-payment-123'
        assert result.status == 'pending'
        assert result.confirmation_url == 'https://yookassa.ru/confirm'
        assert result.raw_response == {'id': 'yk-payment-123', 'status': 'pending'}

    @patch('premium.adapters.yookassa_adapter.Payment')
    def test_create_payment_no_confirmation_url(
        self,
        mock_payment_class: MagicMock,
    ) -> None:
        mock_payment = MagicMock()
        mock_payment.id = 'yk-123'
        mock_payment.status = 'pending'
        mock_payment.confirmation = None
        mock_payment.json.return_value = '{}'
        mock_payment_class.create.return_value = mock_payment

        adapter = YooKassaPaymentAdapter(shop_id='shop', secret_key='secret')
        result = adapter.create_payment(
            amount_value='100',
            currency='RUB',
            description='Test',
            return_url='https://site.com',
            idempotency_key='12345678-1234-5678-1234-567812345678',
        )

        assert result.confirmation_url == ''

    @patch('premium.adapters.yookassa_adapter.Payment')
    def test_create_payment_json_parse_error_returns_empty_dict(
        self,
        mock_payment_class: MagicMock,
    ) -> None:
        mock_payment = MagicMock()
        mock_payment.id = 'yk-123'
        mock_payment.status = 'pending'
        mock_payment.confirmation = MagicMock(confirmation_url='https://pay.ru')
        mock_payment.json.side_effect = TypeError('Not JSON')
        mock_payment_class.create.return_value = mock_payment

        adapter = YooKassaPaymentAdapter(shop_id='shop', secret_key='secret')
        result = adapter.create_payment(
            amount_value='100',
            currency='RUB',
            description='Test',
            return_url='https://site.com',
            idempotency_key='12345678-1234-5678-1234-567812345678',
        )

        assert result.raw_response == {}
