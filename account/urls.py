from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('signin/', views.SignIn.as_view(), name='signin'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('success/', views.signup_success, name='signup_success'),
    path('update/', views.UpdateUser.as_view(), name='update_user'),

    path('profile/', views.Profile_Detail.as_view(), name='profile'),
]
