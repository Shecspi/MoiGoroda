from django.contrib.auth.models import User
from django.http import Http404
from django.views.generic import TemplateView

from account.models import ShareSettings
from utils.LoggingMixin import LoggingMixin


class Share(TemplateView, LoggingMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.can_share_basic_info = None
        self.can_share_city_map = None
        self.can_share_region_map = None
        self.active_page = None
        self.user_id = None

    def get(self, *args, **kwargs):
        self.user_id = kwargs.get('pk')

        # Если пользователь не разрешил делиться своей статистикой, то возвращаем 404.
        # Это происходит в 2 случаях - когда пользователь ни разу не изменял настройки
        # (в таком случае в БД не будет записи), либо если запись имеется, но поле can_share имеет значение False.
        if (ShareSettings.objects.filter(user=self.user_id).count() == 0 or
                not ShareSettings.objects.get(user=self.user_id).can_share):
            self.set_message(self.request, '(Share statistics): Has no permissions from owner to see this page')
            raise Http404

        # Определение активной страницы
        obj = ShareSettings.objects.get(user=self.user_id)
        if obj.can_share_basic_info:
            self.active_page = 'basic_info'
        elif obj.can_share_city_map:
            self.active_page = 'city_map'
        elif obj.can_share_region_map:
            self.active_page = 'region_map'
        else:
            self.set_message(
                self.request,
                '(Share statistics) All share settings are False. Cannot find the HTML-template.'
            )
            raise Http404

        # Определяем доступность кнопок для перехода в определённые пункты статистики
        self.can_share_basic_info = True if obj.can_share_basic_info else False
        self.can_share_city_map = True if obj.can_share_city_map else False
        self.can_share_region_map = True if obj.can_share_region_map else False

        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['username'] = User.objects.get(pk=self.user_id).username
        context['active_page'] = self.active_page
        context['can_share_basic_info'] = self.can_share_basic_info
        context['can_share_city_map'] = self.can_share_city_map
        context['can_share_region_map'] = self.can_share_region_map

        return context

    def get_template_names(self):
        return [f'share/{self.active_page}.html']

