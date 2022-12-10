from django.urls import path

from news import views

urlpatterns = [
    path('', views.News_List.as_view(), name='news-list'),
    path('<int:pk>', views.News_Detail.as_view(), name='news-detail'),
]
