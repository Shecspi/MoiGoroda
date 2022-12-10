import logging
from builtins import set

from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.views.generic import ListView, DetailView
from django.http import Http404

from news.models import News

logger = logging.getLogger('app')


def prepare_log_string(status: int, message: str, request: WSGIRequest) -> str:
    """Возвращает строку, подготовленную для записи в log-файл"""
    return f'{status}: {message} URL: "{request.path}". Method: "{request.method}". User: "{request.user}"'


class News_List(ListView):
    model = News
    template_name = 'news/list.html'


class News_Detail(DetailView):
    model = News
    template_name = 'news/detail.html'

    def get(self, request, *args, **kwargs):
        try:
            news = News.objects.get(id=self.kwargs['pk'])

            # Если пользователь видит эту новость первый раз, то отмечаем её как прочитанную
            if self.request.user.is_authenticated:
                if self.request.user not in news.users_checked.all():
                    news.users_checked.add(self.request.user)
                    news.save()
        except ObjectDoesNotExist:
            logger.warning(
                prepare_log_string(404, 'Attempt to access a non-existent news.', request),
                extra={'classname': self.__class__.__name__}
            )
            raise Http404

        return super().get(request, *args, **kwargs)
