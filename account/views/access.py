"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from __future__ import annotations

import logging
from typing import Any

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, PasswordResetDoneView, PasswordChangeView
from django.http import HttpRequest, HttpResponse, HttpResponseBase

from MoiGoroda.settings import PRIVACY_POLICY_VERSION
from account.forms import SignUpForm, SignInForm
from account.models import UserConsent

logger_email = logging.getLogger(__name__)


class SignUp(CreateView):  # type: ignore[type-arg]
    """
    Отображает и обрабатывает форму регистрации.

    > Авторизованных пользователей перенаправляет в список посещённых городов.
    """

    form_class = SignUpForm
    template_name = 'account/auth/signup.html'

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        if self.request.user.is_authenticated:
            return redirect('city-all-list')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: SignUpForm) -> HttpResponse:
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1'],
            email=form.cleaned_data['email'],
        )
        user.save()

        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')

        UserConsent.objects.create(
            user=user,
            consent_given=True,
            ip_address=ip,
            policy_version=PRIVACY_POLICY_VERSION or '1.0',
        )

        logger_email.info(
            f'Registration of a new user: {form.cleaned_data["username"]} ({form.cleaned_data["email"]}). '
            f'Total numbers of users: {User.objects.count()}'
        )
        login(self.request, user)

        return redirect('city-all-list')

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['page_title'] = 'Регистрация'
        context['page_description'] = (
            'Зарегистрируйтесь на сервисе "Мои города" для того, чтобы сохранять свои '
            'посещённые города и просматривать их на карте'
        )

        return context


class SignIn(LoginView):
    """
    Отображает и обрабатывает форму авторизации.

    > Авторизованных пользователей перенаправляет в список посещённых городов.
    """

    form_class = SignInForm
    template_name = 'account/auth/signin.html'

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        if self.request.user.is_authenticated:
            return redirect('city-all-list')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['page_title'] = 'Вход'
        context['page_description'] = (
            'Войдите в свой аккаунт для того, чтобы посмотреть свои посещённые города '
            'и сохранить новые'
        )

        return context


class MyPasswordChangeView(PasswordChangeView):
    template_name = 'account/password/change/form.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['page_title'] = 'Изменение пароля'
        context['page_description'] = (
            'Для того, чтобы изменить свой пароль, введите старый и новый пароли'
        )

        return context


class MyPasswordResetDoneView(LoginRequiredMixin, PasswordResetDoneView):
    template_name = 'account/password/change/done.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['page_title'] = 'Изменение пароля'
        context['page_description'] = 'Пароль успешно изменён'

        return context
