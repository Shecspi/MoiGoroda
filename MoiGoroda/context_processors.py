import environ
from django.db.models import Q

from news.models import News

env = environ.Env()
environ.Env.read_env()


def general_settings(request):
    # Список ID новостей, которые пользователь уже прочитал
    users_read_news = News.users_read.through.objects.filter(user_id=request.user).values_list('news_id', flat=True)
    # True, если есть хотя бы одна новость, ID которой нет в user_read_news
    has_unread_news = News.objects.filter(~Q(id__in=users_read_news)).exists()

    context = {
        'SITE_NAME': env('SITE_NAME'),
        'PROJECT_VERSION': env('PROJECT_VERSION'),
        'API_YANDEX_MAP': env('API_YANDEX_MAP'),
        'YANDEX_METRIKA': env('YANDEX_METRIKA'),
        'SUPPORT_EMAIL': env('DEFAULT_FROM_EMAIL'),
        'has_unread_news': has_unread_news
    }

    return context
