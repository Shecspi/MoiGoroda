from django.urls import path
from . import views

urlpatterns = [
    # Списки с городами
    path('', views.news, name='news'),
]
