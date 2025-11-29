"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from __future__ import annotations

from typing import Any

from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView


class Dashboard(UserPassesTestMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'

    def test_func(self) -> bool:
        """Проверка что пользователь является суперпользователем."""
        return self.request.user.is_superuser

    def handle_no_permission(self) -> Any:
        raise PermissionDenied()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['page_title'] = 'Dashboard'
        context['page_description'] = ''

        return context
