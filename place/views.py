"""

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

"""

from django.shortcuts import render


def place(request):
    return render(
        request,
        'place/map.html',
        context={
            'page_title': 'Интересные места',
            'page_description': 'Карта интересных мест',
        },
    )
