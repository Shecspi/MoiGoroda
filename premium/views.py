"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def promo(request: HttpRequest) -> HttpResponse:
    """
    Страница с промо-предложением премиум-подписки на сервис.
    Доступна всем пользователям.
    """
    return render(
        request,
        "premium/promo.html",
        context={
            "page_title": "Премиум-подписка на сервис «Мои города»",
            "page_description": (
                "Выберите бесплатный или премиум-тариф на сервис «Мои города» "
                "и поддержите развитие проекта"
            ),
        },
    )

