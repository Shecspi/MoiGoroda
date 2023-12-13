"""
Соотносит URL и методы-отображения приложения Collection.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.CollectionList.as_view(), name='collection-list'),
    path('<int:pk>/list', views.CollectionDetail_List.as_view(), name='collection-detail-list'),
    path('<int:pk>/map', views.CollectionDetail_Map.as_view(), name='collection-detail-map')
]
