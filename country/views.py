"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def country(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        'country/map.html',
        context={
            'page_title': 'Карта стран мира',
            'page_description': 'Карта стран мира',
        },
    )
