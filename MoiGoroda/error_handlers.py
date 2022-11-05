from django.template.response import TemplateResponse


def page403(request, exception):
    return TemplateResponse(
        request,
        'error/403.html',
        status=403
    )


def page404(request, exception):
    return TemplateResponse(
        request,
        'error/404.html',
        status=404
    )


def page500(request):
    return TemplateResponse(
        request,
        'error/500.html',
        status=500
    )
