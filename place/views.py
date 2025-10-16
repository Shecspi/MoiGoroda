"""

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

"""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


@login_required
def place(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        'place/map.html',
        context={
            'page_title': 'Мои места',
            'page_description': 'Мои места, отмеченные на карте',
            'active_page': 'places',
        },
    )
