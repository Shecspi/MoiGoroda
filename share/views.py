"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from enum import auto, StrEnum
from typing import Any, Literal

from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView

from account.models import ShareSettings
from city.models import VisitedCity
from region.models import Region
from services import logger
from services.db.statistics.get_info_for_statistic_cards_and_charts import (
    get_info_for_statistic_cards_and_charts,
)
from services.db.visited_city_repo import get_all_visited_cities
from services.db.regions_repo import get_all_visited_regions


class TypeOfSharedPage(StrEnum):
    """
    Структура данных, которая хранит в себе информацию о трёх возможных типах отображаемых страниц.
    """

    dashboard = auto()
    city_map = auto()
    region_map = auto()


class Share(TemplateView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        # ID пользователя, статистику которого необходимо отобразить
        self.user_id: int | None = None

        # Страница, которую пользователь запрашивает через GET-параметр.
        self.requested_page: Literal['city_map', 'region_map'] | None = None

        # Страница, которая будет отображена пользоватлю после всех проверок.
        # Она может отличаться от запрошенной self.requested_page, так как
        # пользователь мог ограничить отображение какого-то вида информации.
        self.displayed_page: TypeOfSharedPage | None = None

        # Разрешил ли пользователь отображать основную информацию
        self.can_share_dashboard: bool = False

        # Разрешил ли пользователь отображать карту посещённых городов
        self.can_share_city_map: bool = False

        # Разрешил ли пользователь отображать карту посещённых регионов
        self.can_share_region_map: bool = False

        # Разрешил ли пользователь подписываться на него
        self.can_subscribe: bool = False

    def get(self, *args: Any, **kwargs: Any) -> HttpResponse:
        self.user_id = kwargs['pk']

        # Суперпользователь может просматривать статистику любого пользователя вне зависимости от настроек.
        # Поэтому определяем необходимые параметры и пропускаем все проверки.
        if self.request.user.is_authenticated and self.request.user.is_superuser:
            self.displayed_page = kwargs.get('requested_page')
            if not self.displayed_page:
                self.displayed_page = TypeOfSharedPage.dashboard

            self.can_share_dashboard = True
            self.can_share_city_map = True
            self.can_share_region_map = True
            self.can_subscribe = True

            logger.info(
                self.request,
                '(Share statistics) Viewing shared statistics by superuser',
            )

            return super().get(*args, **kwargs)

        # Если пользователь не разрешил делиться своей статистикой, то возвращаем 404.
        # Это происходит в 2 случаях - когда пользователь ни разу не изменял настройки
        # (в таком случае в БД не будет записи), либо если запись имеется, но поле can_share имеет значение False.
        if (
            ShareSettings.objects.filter(user=self.user_id).count() == 0
            or not ShareSettings.objects.get(user=self.user_id).can_share
        ):
            logger.warning(
                self.request,
                '(Share statistics): Has no permissions from owner to see this page',
            )
            raise Http404

        settings = ShareSettings.objects.get(user=self.user_id)

        # Если по каким-то причинам оказалось так, что все три возможных страницы для отображения
        # в БД указаны как False, то возвращаем 404. Хотя такого быть не должно. Но на всякий случай проверил.
        if (
            not settings.can_share_dashboard
            and not settings.can_share_city_map
            and not settings.can_share_region_map
        ):
            logger.warning(
                self.request,
                '(Share statistics) All share settings are False. I do not know what to show.',
            )
            raise Http404

        self.requested_page = kwargs.get('requested_page', None)

        # Если URL имеет вид /share/1, то отображаем общую информацию
        if not self.requested_page:
            self.requested_page = TypeOfSharedPage.dashboard

        # Если в URL указан неподдерживаемый параметр 'requested_page', то возвращаем 404.
        if self.requested_page not in TypeOfSharedPage:
            logger.warning(
                self.request,
                '(Share statistics) Invalid GET-parameter "requested_page"',
            )
            raise Http404

        # Определяем страницу, которую необходимо отобразить
        self.displayed_page = get_displayed_page(self.requested_page, settings)
        if self.displayed_page != self.requested_page:
            if self.displayed_page == TypeOfSharedPage.dashboard:
                return redirect('share', pk=self.user_id)
            else:
                return redirect('share', pk=self.user_id, requested_page=self.displayed_page.value)
        if not self.displayed_page:
            logger.warning(
                self.request,
                '(Share statistics) All share settings are False. Cannot find the HTML-template.',
            )
            raise Http404

        # Определяем доступность кнопок для перехода в определённые пункты статистики
        self.can_share_dashboard = True if settings.can_share_dashboard else False
        self.can_share_city_map = True if settings.can_share_city_map else False
        self.can_share_region_map = True if settings.can_share_region_map else False
        self.can_subscribe = True if settings.can_subscribe else False

        logger.info(self.request, '(Share statistics) Viewing shared statistics')

        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['username'] = User.objects.get(pk=self.user_id).username
        context['user_id'] = self.user_id
        context['displayed_page'] = self.displayed_page
        context['can_share_dashboard'] = self.can_share_dashboard
        context['can_share_city_map'] = self.can_share_city_map
        context['can_share_region_map'] = self.can_share_region_map
        context['can_subscribe'] = self.can_subscribe
        context['is_subscribed'] = True
        context['page_title'] = f'Статистика пользователя {context["username"]}'
        context['page_description'] = (
            f'Статистика посещённых городов и регионов пользователя {context["username"]}'
        )

        if self.displayed_page == TypeOfSharedPage.dashboard:
            context = context | get_info_for_statistic_cards_and_charts(self.user_id)
        elif self.displayed_page == TypeOfSharedPage.city_map:
            context = context | additional_context_for_city_map(self.user_id)
        elif self.displayed_page == TypeOfSharedPage.region_map:
            context = context | additional_context_for_region_map(self.user_id)
        else:
            logger.info(
                self.request,
                '(Share statistics) All share settings are False. Cannot find the context generator.',
            )
            raise Http404

        return context

    def get_template_names(self) -> list[str]:
        return [f'share/{self.displayed_page}.html']


def get_displayed_page(requested_page: str, settings: ShareSettings) -> TypeOfSharedPage | None:
    """
    Возвращает страницу, которую необходимо отобразить пользователю на основе запрошенной страницы requested_page
    и настроек settings, сохранённых в базе данных. Если запрошенная страница не доступна для отображения,
    соответственно настройкам БД, то выбираются другие на основе приоритетности. Если и они не доступны для отображения,
    то возвращается False.
    """
    displayed_page = None

    if requested_page == TypeOfSharedPage.dashboard:
        if settings.can_share_dashboard:
            displayed_page = TypeOfSharedPage.dashboard
        elif settings.can_share_city_map:
            displayed_page = TypeOfSharedPage.city_map
        elif settings.can_share_region_map:
            displayed_page = TypeOfSharedPage.region_map
    elif requested_page == TypeOfSharedPage.city_map:
        if settings.can_share_city_map:
            displayed_page = TypeOfSharedPage.city_map
        elif settings.can_share_dashboard:
            displayed_page = TypeOfSharedPage.dashboard
        elif settings.can_share_region_map:
            displayed_page = TypeOfSharedPage.region_map
    elif requested_page == TypeOfSharedPage.region_map:
        if settings.can_share_region_map:
            displayed_page = TypeOfSharedPage.region_map
        elif settings.can_share_dashboard:
            displayed_page = TypeOfSharedPage.dashboard
        elif settings.can_share_city_map:
            displayed_page = TypeOfSharedPage.city_map

    return displayed_page


def additional_context_for_city_map(user_id: int) -> dict[str, QuerySet[VisitedCity]]:
    """
    Получает из БД все города, которые посетил пользователь с ID user_id и возвращает их в виде словаря.
    """
    return {'all_cities': get_all_visited_cities(user_id)}


def additional_context_for_region_map(user_id: int) -> dict[str, QuerySet[Region]]:
    """
    Получает из БД все регионы, которые посетил пользователь с ID user_id и возвращает их в виде словаря.
    """
    return {'all_regions': get_all_visited_regions(user_id)}
