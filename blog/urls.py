"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.BlogArticleList.as_view(), name='blog-list'),
    path('tag/<slug:tag_slug>/', views.BlogArticleList.as_view(), name='blog-list-by-tag'),
    path('<int:pk>/', views.BlogArticleDetail.as_view(), name='blog-article-detail'),
]
