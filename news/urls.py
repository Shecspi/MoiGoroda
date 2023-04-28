"""
Соотносит URL и методы-отображения приложения News.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.NewsList.as_view(), name='news-list'),
]
