import logging

from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.template.response import TemplateResponse
from django.views import View


class ExceptionHandler(View):
    """Базовый класс для логирования исключений."""
    logger = logging.getLogger('app')

    def raise404(self, request):
        self.logger.warning(f'Page not found: "{request.path}", user: "{request.user}"')
        raise Http404

    def raise403(self, request):
        self.logger.warning(f'Permisson denied: "{request.path}", user: "{request.user}"')
        raise PermissionDenied()


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
