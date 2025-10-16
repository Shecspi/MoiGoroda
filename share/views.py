"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any, Literal

from django.views.generic import TemplateView

from share.service import ShareService
from share.structs import TypeOfSharedPage


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

        # Подписан ли пользователь на выбранного пользователя
        self.is_subscribed: bool = False
        self.country_code: str | None = None

    def dispatch(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        self.service = ShareService(
            request,
            user_id=kwargs['pk'],
            requested_page=kwargs.get('requested_page'),
            country_code=request.GET.get('country'),
        )

        redirect_response = self.service.handle_redirects_if_needed()
        if redirect_response:
            return redirect_response

        self.service.check_permissions_and_get_settings()
        self.service.determine_displayed_page()
        self.service.resolve_country_if_needed()

        redirect_response = self.service.maybe_redirect_to_valid_page()
        if redirect_response:
            return redirect_response

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        super().get_context_data(**kwargs)
        return self.service.get_context()

    def get_template_names(self) -> list[str]:
        return [self.service.get_template_name()]
