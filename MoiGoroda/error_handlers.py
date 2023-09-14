from django.template.response import TemplateResponse


def page403(request, exception):
    return TemplateResponse(
        request,
        'error/403.html',
        status=403,
        context={
            'page_title': 'Отказано в доступе'
        }
    )


def page404(request, exception):
    return TemplateResponse(
        request,
        'error/404.html',
        status=404,
        context={
            'page_title': 'Страница не найдена'
        }
    )


def page500(request):
    return TemplateResponse(
        request,
        'error/500.html',
        status=500,
        context={
            'page_title': 'Внутренняя ошибка'
        }
    )
