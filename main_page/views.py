from django.shortcuts import redirect, render


def index(request):
    if request.user.is_authenticated:
        return redirect('city-all-list')
    else:
        return render(
            request,
            'index.html',
            context={
                'page_title': 'Сервис учёта посещённых городов «Мои города»',
                'page_description': "«Мои города» — сервис учёта посещённых городов: отмечайте города и страны, смотрите их на карте, открывайте новые направления и следите за поездками друзей",
            },
        )
