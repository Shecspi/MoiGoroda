import json
from typing import Any

from django.contrib.auth.models import User
from django.http import Http404, HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.safestring import mark_safe

from account.models import ShareSettings
from city.services.db import get_unique_visited_cities
from country.models import Country
from region.services.db import get_all_region_with_visited_cities
from services.db.statistics.get_info_for_statistic_cards_and_charts import (
    get_info_for_statistic_cards_and_charts,
)
from share.structs import TypeOfSharedPage
from subscribe.repository import is_subscribed


class ShareService:
    def __init__(
        self,
        request: HttpRequest,
        user_id: int,
        requested_page: str | None,
        country_code: str | None,
    ) -> None:
        self.request = request
        self.user_id = user_id
        self.requested_page = requested_page
        self.country_code = country_code
        self.displayed_page: TypeOfSharedPage | None = None

        self.country: str | None = None
        self.country_id: int | None = None

        self.settings: ShareSettings | None = None

    def handle_redirects_if_needed(self) -> HttpResponseRedirect | None:
        if self.requested_page == TypeOfSharedPage.region_map and not self.country_code:
            return redirect(reverse('share', kwargs={'pk': self.user_id}) + 'region_map?country=RU')
        return None

    def check_permissions_and_get_settings(self) -> None:
        if not ShareSettings.objects.filter(user=self.user_id).exists():
            raise Http404('No sharing settings found.')

        self.settings = ShareSettings.objects.get(user=self.user_id)

        if not (
            self.settings.can_share_dashboard
            or self.settings.can_share_city_map
            or self.settings.can_share_region_map
        ):
            raise Http404('User has disabled all sharing options.')

    def determine_displayed_page(self) -> TypeOfSharedPage:
        if self.settings is None:
            raise Http404('Settings not initialized.')
        self.displayed_page = get_displayed_page(self.requested_page, self.settings)
        if not self.displayed_page:
            raise Http404('No available page to display.')
        return self.displayed_page

    def maybe_redirect_to_valid_page(self) -> HttpResponseRedirect | None:
        if self.displayed_page != self.requested_page:
            if self.displayed_page is None:
                return None
            # if self.displayed_page == TypeOfSharedPage.dashboard:
            #     return redirect('share', pk=self.user_id, requested_page=self.displayed_page.value)
            return redirect('share', pk=self.user_id, requested_page=self.displayed_page.value)
        return None

    def resolve_country_if_needed(self) -> None:
        if self.displayed_page == TypeOfSharedPage.region_map:
            try:
                country = Country.objects.get(code=self.country_code)
                self.country = str(country)
                self.country_id = country.id
            except Country.DoesNotExist:
                raise Http404('Country does not exist.')

    def get_context(self) -> dict[str, Any]:
        if self.settings is None:
            raise Http404('Settings not initialized.')

        user = User.objects.get(pk=self.user_id)
        current_user_id = self.request.user.id if self.request.user.is_authenticated else 0
        context: dict[str, Any] = {
            'country_code': self.country_code,
            'username': user.username,
            'user_id': self.user_id,
            'displayed_page': self.displayed_page,
            'can_share_dashboard': self.settings.can_share_dashboard,
            'can_share_city_map': self.settings.can_share_city_map,
            'can_share_region_map': self.settings.can_share_region_map,
            'can_subscribe': self.settings.can_subscribe,
            'is_subscribed': is_subscribed(current_user_id, self.user_id),
            'page_title': f'Статистика пользователя {user.username}',
            'page_description': f'Статистика посещённых городов и регионов пользователя {user.username}',
        }

        if self.displayed_page == TypeOfSharedPage.dashboard:
            context |= get_info_for_statistic_cards_and_charts(self.user_id)
        elif self.displayed_page == TypeOfSharedPage.city_map:
            cities = get_unique_visited_cities(self.user_id)
            cities_data = [
                {
                    'name': c.city.title,
                    'lat': float(str(c.city.coordinate_width).replace(',', '.')),
                    'lon': float(str(c.city.coordinate_longitude).replace(',', '.')),
                }
                for c in cities
            ]
            context['all_cities'] = mark_safe(json.dumps(cities_data))
        elif self.displayed_page == TypeOfSharedPage.region_map:
            context['all_regions'] = get_all_region_with_visited_cities(
                self.user_id, self.country_id
            )
            context['number_of_regions'] = len(context['all_regions'])

        return context

    def get_template_name(self) -> str:
        return f'share/{self.displayed_page}.html'


def get_displayed_page(
    requested_page: str | None, settings: ShareSettings
) -> TypeOfSharedPage | None:
    """
    Возвращает страницу, которую нужно отобразить на основе запроса и доступных настроек.
    Приоритет: сначала пробуем запрошенную, затем альтернативные по заранее заданному порядку.
    """
    try:
        requested_enum = TypeOfSharedPage(requested_page) if requested_page else None
    except ValueError:
        requested_enum = None

    available_pages = {
        TypeOfSharedPage.dashboard: settings.can_share_dashboard,
        TypeOfSharedPage.city_map: settings.can_share_city_map,
        TypeOfSharedPage.region_map: settings.can_share_region_map,
    }

    # приоритет отображения в зависимости от запроса
    priorities = {
        TypeOfSharedPage.dashboard: [
            TypeOfSharedPage.dashboard,
            TypeOfSharedPage.city_map,
            TypeOfSharedPage.region_map,
        ],
        TypeOfSharedPage.city_map: [
            TypeOfSharedPage.city_map,
            TypeOfSharedPage.dashboard,
            TypeOfSharedPage.region_map,
        ],
        TypeOfSharedPage.region_map: [
            TypeOfSharedPage.region_map,
            TypeOfSharedPage.dashboard,
            TypeOfSharedPage.city_map,
        ],
    }

    # Если нет запроса — проверим по любому доступному
    if not requested_enum:
        for page, can_share in available_pages.items():
            if can_share:
                return page
        return None

    # Если запрошенная страница не входит в приоритеты — вернём None
    if requested_enum not in priorities:
        return None

    for page in priorities[requested_enum]:
        if available_pages[page]:
            return page

    return None
