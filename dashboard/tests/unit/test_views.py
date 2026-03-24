"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from __future__ import annotations

import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.test import RequestFactory

from dashboard.views import dashboard


@pytest.mark.django_db
@pytest.mark.unit
def test_dashboard_allows_superuser(django_user_model: type) -> None:
    user = django_user_model.objects.create_superuser('admin', 'a@a.com', 'pw')
    rf = RequestFactory()
    request = rf.get('/dashboard/')
    request.user = user
    response = dashboard(request)
    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.unit
def test_dashboard_denies_non_superuser(django_user_model: type) -> None:
    user = django_user_model.objects.create_user('user', 'u@u.com', 'pw')
    rf = RequestFactory()
    request = rf.get('/dashboard/')
    request.user = user
    with pytest.raises(PermissionDenied):
        dashboard(request)


@pytest.mark.unit
def test_dashboard_redirects_anonymous_to_login() -> None:
    rf = RequestFactory()
    request = rf.get('/dashboard/')
    request.user = AnonymousUser()
    response = dashboard(request)
    assert response.status_code == 302
    assert isinstance(response, HttpResponseRedirect)
