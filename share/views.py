from django.contrib.auth.models import User
from django.http import Http404
from django.views.generic import TemplateView

from account.models import ShareSettings
from services.db.statistics.get_info_for_statistic_cards_and_charts import *
from utils.LoggingMixin import LoggingMixin


class Share(TemplateView, LoggingMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request_type = None
        self.can_share_basic_info = None
        self.can_share_city_map = None
        self.can_share_region_map = None
        self.statistics_block = None
        self.user_id = None

    def get(self, *args, **kwargs):
        self.user_id = kwargs.get('pk')
        self.request_type = kwargs.get('request_type')

        # Если пользователь не разрешил делиться своей статистикой, то возвращаем 404.
        # Это происходит в 2 случаях - когда пользователь ни разу не изменял настройки
        # (в таком случае в БД не будет записи), либо если запись имеется, но поле can_share имеет значение False.
        if (ShareSettings.objects.filter(user=self.user_id).count() == 0 or
                not ShareSettings.objects.get(user=self.user_id).can_share):
            self.set_message(self.request, '(Share statistics): Has no permissions from owner to see this page')
            raise Http404

        obj = ShareSettings.objects.get(user=self.user_id)

        # Определение активной страницы
        # Если request_type в URL не указан, то смотрим, какие страницы пользователь разрешил показывать.
        # Обрабатываем их в порядке приоритетности - страница с общей информацией, карта городов, карта регионов.
        if not self.request_type:
            if obj.can_share_basic_info:
                self.statistics_block = 'basic_info'
            elif obj.can_share_city_map:
                self.statistics_block = 'city_map'
            elif obj.can_share_region_map:
                self.statistics_block = 'region_map'
            else:
                self.set_message(
                    self.request,
                    '(Share statistics) All share settings are False. Cannot find the HTML-template.'
                )
                raise Http404
        # Если request_type указан, то он должен быть одним из двух - 'city_map' или 'region_map',
        # а также в БД должна быть включена соответствующая н9астройка.
        elif self.request_type == 'city_map' and obj.can_share_city_map:
            self.statistics_block = 'city_map'
        elif self.request_type == 'region_map' and obj.can_share_region_map:
            self.statistics_block = 'region_map'
        # Если совпадений нет, то возвращаем 404.
        else:
            self.set_message(
                self.request,
                '(Share statistics) Cannot find a match between the request_type and active_page.'
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
        context['user_id'] = self.user_id
        context['statistics_block'] = self.statistics_block
        context['can_share_basic_info'] = self.can_share_basic_info
        context['can_share_city_map'] = self.can_share_city_map
        context['can_share_region_map'] = self.can_share_region_map

        if self.statistics_block == 'basic_info':
            result = context | get_info_for_statistic_cards_and_charts(self.user_id)
        elif self.statistics_block == 'city_map':
            result = context
        elif self.statistics_block == 'region_map':
            result = context
        else:
            self.set_message(
                self.request,
                '(Share statistics) All share settings are False. Cannot find the context generator.'
            )
            raise Http404

        return result

    def get_template_names(self):
        return [f'share/{self.statistics_block}.html']

