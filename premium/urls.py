from django.urls import path

from premium.views import checkout, promo, success


urlpatterns = [
    path('plans/', promo, name='premium_promo'),
    path('checkout/', checkout, name='premium_checkout'),
    path('success/', success, name='premium_success'),
]
