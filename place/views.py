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
