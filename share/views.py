import enum
from enum import auto, EnumMeta
from typing import Literal, TypeAlias

from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import Http404
from django.views.generic import TemplateView

from account.models import ShareSettings
from city.models import VisitedCity
from region.models import Region
from services.db.statistics.get_info_for_statistic_cards_and_charts import get_info_for_statistic_cards_and_charts
from services.db.visited_cities import get_all_visited_cities
from services.db.visited_regions import get_all_visited_regions
from utils.LoggingMixin import LoggingMixin


class MetaEnum(EnumMeta):
    """
    Этот дополнительный класс нужен для того, чтобы дочерний Enum-класс мог проверять вхождение строки по 'in'.
    """
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class TypeOfSharePage(enum.StrEnum, metaclass=MetaEnum):
    dashboard = auto()
    city_map = auto()
    region_map = auto()


DisplayedPageType: TypeAlias = Literal['dashboard', 'city_map', 'region_map', False]


def get_displayed_page(requested_page: str, settings: ShareSettings) -> DisplayedPageType:
    """
    Возвращает страницу, которую необходимо отобразить пользователю на основе запрошенной страницы requested_page
    и настроек settings, сохранённых в базе данных. Если запрошенная страница не доступна для отображения,
    соответственно настройкам БД, то выбираются другие на основе приоритетности. Если и они не доступны для отображения,
    то возвращается False.
    """
    displayed_page: DisplayedPageType = False

    if requested_page == TypeOfSharePage.dashboard:
        if settings.can_share_dashboard:
            displayed_page = 'dashboard'
        elif settings.can_share_city_map:
            displayed_page = 'city_map'
        elif settings.can_share_region_map:
            displayed_page = 'region_map'
    elif requested_page == TypeOfSharePage.city_map:
        if settings.can_share_city_map:
            displayed_page = 'city_map'
        elif settings.can_share_dashboard:
            displayed_page = 'dashboard'
        elif settings.can_share_region_map:
            displayed_page = 'region_map'
    elif requested_page == TypeOfSharePage.region_map:
        if settings.can_share_region_map:
            displayed_page = 'region_map'
        elif settings.can_share_dashboard:
            displayed_page = 'dashboard'
        elif settings.can_share_region_map:
            displayed_page = 'city_map'

    return displayed_page


class Share(TemplateView, LoggingMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # ID пользователя, статистику которого необходимо отобразить
        self.user_id = None

        # Страница, которую пользователь запрашивает через GET-параметр
        self.requested_page = None

        # Страница, которая будет отображена пользоватлю после всех проверок.
        # Она может отличаться от запрошенной self.requested_page, так как
        # пользователь мог ограничить отображение какого-то вида информации.
        self.displayed_page: str | None = None

        # Разрешил ли пользователь отображать основную информацию
        self.can_share_dashboard: bool = False

        # Разрешил ли пользователь отображать карту посещённых городов
        self.can_share_city_map: bool = False

        # Разрешил ли пользователь отображать карту посещённых регионов
        self.can_share_region_map: bool = False

    def get(self, *args, **kwargs):
        self.user_id = kwargs.get('pk')

        # Если пользователь не разрешил делиться своей статистикой, то возвращаем 404.
        # Это происходит в 2 случаях - когда пользователь ни разу не изменял настройки
        # (в таком случае в БД не будет записи), либо если запись имеется, но поле can_share имеет значение False.
        if (ShareSettings.objects.filter(user=self.user_id).count() == 0 or
                not ShareSettings.objects.get(user=self.user_id).can_share):
            self.set_message(self.request, '(Share statistics): Has no permissions from owner to see this page')
            raise Http404

        settings = ShareSettings.objects.get(user=self.user_id)

        # Если по каким-то причинам оказалось так, что все три возможных страницы для отображения
        # в БД указаны как False, то возвращаем 404. Хотя такого быть не должно. Но на всякий случай проверил.
        if not settings.can_share_dashboard and not settings.can_share_city_map and not settings.can_share_region_map:
            self.set_message(
                self.request,
                '(Share statistics) All share settings are False. I do not know what to show.'
            )
            raise Http404

        self.requested_page = kwargs.get('requested_page')

        # Если URL имеет вид /share/1, то отображаем общую информацию
        if not self.requested_page:
            self.requested_page = TypeOfSharePage.dashboard

        # Если в URL указан неподдерживаемый параметр 'requested_page', то возвращаем 404.
        if self.requested_page not in TypeOfSharePage:
            self.set_message(
                self.request,
                "(Share statistics) Invalid GET-parameter 'requested_page'"
            )
            raise Http404

        # Определяем страницу, которую необходимо отобразить
        self.displayed_page = get_displayed_page(self.requested_page, settings)
        if not self.displayed_page:
            self.set_message(
                self.request,
                '(Share statistics) All share settings are False. Cannot find the HTML-template.'
            )
            raise Http404

        # Определяем доступность кнопок для перехода в определённые пункты статистики
        self.can_share_dashboard = True if settings.can_share_dashboard else False
        self.can_share_city_map = True if settings.can_share_city_map else False
        self.can_share_region_map = True if settings.can_share_region_map else False

        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['username'] = User.objects.get(pk=self.user_id).username
        context['user_id'] = self.user_id
        context['displayed_page'] = self.displayed_page
        context['can_share_dashboard'] = self.can_share_dashboard
        context['can_share_city_map'] = self.can_share_city_map
        context['can_share_region_map'] = self.can_share_region_map

        if self.displayed_page == TypeOfSharePage.dashboard:
            result = context | get_info_for_statistic_cards_and_charts(self.user_id)
        elif self.displayed_page == TypeOfSharePage.city_map:
            result = context | additional_context_for_city_map(self.user_id)
        elif self.displayed_page == TypeOfSharePage.region_map:
            result = context | additional_context_for_region_map(self.user_id)
        else:
            self.set_message(
                self.request,
                '(Share statistics) All share settings are False. Cannot find the context generator.'
            )
            raise Http404

        return result

    def get_template_names(self):
        return [f'share/{self.displayed_page}.html']


def additional_context_for_city_map(user_id: int) -> dict[str, QuerySet[VisitedCity]]:
    """
    Получает из БД все города, которые посетил пользователь с ID user_id и возвращает их в виде словаря.
    """
    return {
        'all_cities': get_all_visited_cities(user_id)
    }


def additional_context_for_region_map(user_id: int) -> dict[str, QuerySet[Region]]:
    """
    Получает из БД все регионы, которые посетил пользователь с ID user_id и возвращает их в виде словаря.
    """
    return {
        'all_regions': get_all_visited_regions(user_id)
    }
