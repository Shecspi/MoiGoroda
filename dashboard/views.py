"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    """Страница dashboard только для суперпользователей."""
    if not request.user.is_superuser:
        raise PermissionDenied()

    return render(
        request,
        'dashboard/dashboard.html',
        {
            'page_title': 'Dashboard',
            'page_description': '',
        },
    )
