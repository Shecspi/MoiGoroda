from django.urls import path

from premium.views import promo


urlpatterns = [
    path('plans/', promo, name='premium_promo'),
]
