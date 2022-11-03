from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

from MoiGoroda import settings
from . import views

urlpatterns = [
    path('signin/', views.SignIn.as_view(), name='signin'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('signup/success/', views.signup_success, name='signup_success'),

    path('logout/', LogoutView.as_view(), name='logout'),

    path('profile/', views.Profile_Detail.as_view(), name='profile'),
    path('profile/update/', views.UpdateUser.as_view(), name='update_user'),

    # -----  Сброс пароля  ----- #
    path('password/reset',
         auth_views.PasswordResetView.as_view(
             template_name='account/password/reset/form.html',
             from_email=settings.EMAIL_HOST_USER
         ),
         name='reset_password'
         ),
    path('password/reset/email_sent',
         auth_views.PasswordResetDoneView.as_view(
             template_name='account/password/reset/email_sent.html'
         ),
         name='password_reset_done'
         ),
    path('password/reset/<uidb64>/<token>',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='account/password/reset/new_password.html'
         ),
         name='password_reset_confirm'
         ),
    path('password/reset/done',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='account/password/reset/done.html'
         ),
         name='password_reset_complete'
         ),

    # -----  Изменение пароля  ----- #
    path('password/change/',
         auth_views.PasswordChangeView.as_view(
             template_name='account/password/change/form.html'
         ),
         name='password_change_form'
         ),
    path('password/change/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='account/password/change/done.html'
         ),
         name='password_change_done'
         )
]
