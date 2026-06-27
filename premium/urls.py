# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

from django.urls import path

from premium.views import (
    checkout,
    my_subscription,
    promo,
    subscriptions_management,
    success,
)
from premium.webhook import yookassa_webhook


urlpatterns = [
    path('plans/', promo, name='premium_promo'),
    path('my-subscription/', my_subscription, name='premium_my_subscription'),
    path('subscriptions/', subscriptions_management, name='premium_subscriptions_management'),
    path('checkout/', checkout, name='premium_checkout'),
    path('success/', success, name='premium_success'),
    path('webhook/yookassa/', yookassa_webhook, name='premium_webhook_yookassa'),
]
