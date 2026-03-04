"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from django.contrib.admin.sites import site
from django.contrib.auth.models import User

from premium.admin import (
    PremiumPlanAdmin,
    PremiumPlanFeatureInline,
    PremiumPaymentWebhookLogInline,
)
from premium.models import (
    PremiumPayment,
    PremiumPaymentWebhookLog,
    PremiumPlan,
    PremiumSubscription,
)


@pytest.mark.integration
@pytest.mark.django_db
class TestPremiumAdmin:
    """Тесты регистрации моделей в админке."""

    def test_premium_plan_admin_registered(self) -> None:
        assert site.is_registered(PremiumPlan)

    def test_premium_plan_feature_inline(self) -> None:
        assert PremiumPlanFeatureInline in PremiumPlanAdmin.inlines

    def test_premium_subscription_admin_registered(self) -> None:
        assert site.is_registered(PremiumSubscription)

    def test_premium_payment_admin_registered(self) -> None:
        assert site.is_registered(PremiumPayment)

    def test_premium_payment_webhook_log_admin_registered(self) -> None:
        assert site.is_registered(PremiumPaymentWebhookLog)

    def test_webhook_log_inline_has_no_add_permission(
        self,
        premium_payment: PremiumPayment,
    ) -> None:
        inline = PremiumPaymentWebhookLogInline(
            PremiumPayment,
            site,
        )
        request = type('Request', (), {'user': User()})()
        assert inline.has_add_permission(request, premium_payment) is False


@pytest.mark.integration
@pytest.mark.django_db
class TestPremiumAdminList:
    """Тесты отображения списков в админке."""

    def test_premium_plan_admin_list_display(self) -> None:
        assert 'name' in PremiumPlanAdmin.list_display
        assert 'slug' in PremiumPlanAdmin.list_display
        assert 'price_month' in PremiumPlanAdmin.list_display
