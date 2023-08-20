from django.shortcuts import render


def index(request):
    return render(request, 'index.html', context={
        'page_title': 'Сервис контроля посещённых городов',
        'page_description': 'С помощью сервиса "Мои города" Вы сможете сохранить все свои посещённые города и в любой момент просматривать их на карте России с любого устройства.'
    })
