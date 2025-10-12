"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from __future__ import annotations

from typing import Any

from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView

from account.forms import UpdateProfileForm
from account.repository import get_subscribed_users, get_subscriber_users
from services import logger


class Profile(LoginRequiredMixin, UpdateView):  # type: ignore[type-arg]
    form_class = UpdateProfileForm
    success_url = reverse_lazy('profile')
    template_name = 'account/profile.html'

    def get_object(self, queryset: QuerySet[User] | None = None) -> User:
        """
        Убирает необходимость указывать ID пользователя в URL, используя сессионный ID.
        """
        return get_object_or_404(User, pk=self.request.user.pk)

    def form_valid(self, form: UpdateProfileForm) -> HttpResponse:
        """
        Переопределение этого метода нужно только для того, чтобы произвести запись в лог.
        """
        user = self.request.user
        if isinstance(user, User):
            logger.info(
                self.request,
                f"Updating user's information: {user.username} ({user.email})",
            )
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        user_id = self.request.user.id
        if user_id is not None:
            context['subscribed_users'] = get_subscribed_users(user_id)
            context['subscriber_users'] = get_subscriber_users(user_id)
        else:
            context['subscribed_users'] = []
            context['subscriber_users'] = []

        context['number_of_subscribed_users'] = len(context['subscribed_users'])
        context['number_of_subscriber_users'] = len(context['subscriber_users'])

        context['active_page'] = 'profile'
        context['page_title'] = 'Профиль'
        context['page_description'] = 'Просмотр и изменения персональной информации'

        return context
