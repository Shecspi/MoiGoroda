from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('signin/', views.SignIn.as_view(), name='signin'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('success/', views.signup_success, name='signup_success'),
    path('update/', views.UpdateUser.as_view(), name='update_user'),

    path('profile/', views.Profile_Detail.as_view(), name='profile'),

    path('password/reset',
         auth_views.PasswordResetView.as_view(template_name="account/password/email_form.html"),
         name='reset_password'),
    path('password/email_sent',
         auth_views.PasswordResetDoneView.as_view(template_name="account/password/email_sent.html"),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>',
         auth_views.PasswordResetConfirmView.as_view(template_name="account/password/password_form.html"),
         name='password_reset_confirm'),
    path('password/changed',
         auth_views.PasswordResetCompleteView.as_view(template_name="account/password/password_changed.html"),
         name='password_reset_complete')
]
