from django.contrib.auth.decorators import user_passes_test
from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

from . import views
from .views import MyPasswordResetDoneView, MyPasswordChangeView

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
             template_name='account/profile__password_reset__form.html',
             extra_context={
                 'page_title': 'Восстановление пароля',
                 'page_description': 'Восстановленеи пароля'
             }
         ),
         name='reset_password'
         ),
    path('password/reset/email_sent',
         auth_views.PasswordResetDoneView.as_view(
             template_name='account/profile__password_reset__email_sent.html',
             extra_context={
                 'page_title': 'Восстановление пароля',
                 'page_description': 'Восстановленеи пароля'
             }
         ),
         name='password_reset_done'
         ),
    path('password/reset/<uidb64>/<token>',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='account/profile__password_reset__new_password_form.html',
             extra_context={
                 'page_title': 'Восстановление пароля',
                 'page_description': 'Восстановленеи пароля'
             }
         ),
         name='password_reset_confirm'
         ),
    path('password/reset/done',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='account/profile__password_reset__done.html',
             extra_context={
                 'page_title': 'Восстановление пароля',
                 'page_description': 'Восстановленеи пароля'
             }
         ),
         name='password_reset_complete'
         ),

    # -----  Изменение пароля  ----- #
    path('password/change/', MyPasswordChangeView.as_view(), name='password_change_form'),
    path('password/change/done/', MyPasswordResetDoneView.as_view(), name='password_change_done')
]
