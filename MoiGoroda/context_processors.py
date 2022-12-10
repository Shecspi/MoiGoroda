import environ

from news.models import News

env = environ.Env()
environ.Env.read_env()


def general_settings(request):
    # Проверяем, есть ли непрочитанные новости для отображения этой информации в навбаре
    has_news = False
    if request.user.is_authenticated:
        news = News.objects.all().only('users_checked')

        for n in news:
            if request.user not in n.users_checked.all():
                has_news = True
                break

    context = {
        'SITE_NAME': env('SITE_NAME'),
        'API_YANDEX_MAP': env('API_YANDEX_MAP'),
        'YANDEX_METRIKA': env('YANDEX_METRIKA'),
        'has_news': has_news
    }

    return context
