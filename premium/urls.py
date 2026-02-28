from django.urls import path

from premium.views import checkout, promo, success
from premium.webhook import yookassa_webhook


urlpatterns = [
    path('plans/', promo, name='premium_promo'),
    path('checkout/', checkout, name='premium_checkout'),
    path('success/', success, name='premium_success'),
    path('webhook/yookassa/', yookassa_webhook, name='premium_webhook_yookassa'),
]
