"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from account.models import ShareSettings
from services import logger
from services.db.statistics.fake_statistics import get_fake_statistics
from services.db.statistics.get_info_for_statistic_cards_and_charts import (
    get_info_for_statistic_cards_and_charts,
)
from services.db.statistics.visited_city import get_number_of_visited_cities


class Statistics(LoginRequiredMixin, TemplateView):
    """
    Отображает страницу со статистикой пользователя.

    ID пользователя берётся из сессии, поэтому просмотр данных другого пользователя недоступен.

    > Доступ на эту страницу возможен только авторизованным пользователям.
    """

    template_name = 'account/statistics/statistics.html'

    def get(self, *args, **kwargs):
        logger.info(
            self.request, f'Viewing stats: {self.request.user.username} ({self.request.user.email})'
        )

        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.pk

        number_of_visited_cities = get_number_of_visited_cities(user_id)
        if number_of_visited_cities == 0:
            context['fake_statistics'] = True
            context.update(get_fake_statistics())

            return context

        ##############################################
        # --- Настройки "Поделиться статистикой" --- #
        ##############################################
        try:
            obj = ShareSettings.objects.get(user=self.request.user)
        except ShareSettings.DoesNotExist:
            share_settings = {
                'switch_share_general': False,
                'switch_share_basic_info': False,
                'switch_share_city_map': False,
                'switch_share_region_map': False,
            }
        else:
            share_settings = {
                'switch_share_general': obj.can_share,
                'switch_share_basic_info': obj.can_share_dashboard,
                'switch_share_city_map': obj.can_share_city_map,
                'switch_share_region_map': obj.can_share_region_map,
            }
        context['share_settings'] = share_settings

        ##################################
        # --- Вспомогательные данные --- #
        ##################################

        context['active_page'] = 'stats'
        context['page_title'] = 'Личная статистика'
        context['page_description'] = (
            'Здесь отображается подробная информация о результатах Ваших путешествий'
            ' - посещённые города, регионы и федеральнаые округа'
        )

        return context | get_info_for_statistic_cards_and_charts(user_id)


@login_required()
def save_share_settings(request):
    """
    Производит проверку данных, переданных из формы настроек "Поделиться статистикой" и сохраняет их в БД.
    В таблице для каждого пользователя может быть только одна запись с настройками.
    Поэтому данная функция либо обновляет эту запись, либо создаёт новую, если её ещё нет.
    """

    if request.method == 'POST':
        user = get_object_or_404(User, pk=request.user.pk)

        share_data = request.POST.dict()
        switch_share_general = True if share_data.get('switch_share_general') else False
        switch_share_dashboard = True if share_data.get('switch_share_dashboard') else False
        switch_share_city_map = True if share_data.get('switch_share_city_map') else False
        switch_share_region_map = True if share_data.get('switch_share_region_map') else False

        # В ситуации, когда основной чекбокс включён, а все остальные выключены, возвращаем ошибку,
        # так как не понятно, как конкретно обрабатывать такую ситуацию.
        if switch_share_general and not any(
            [switch_share_dashboard, switch_share_city_map, switch_share_region_map]
        ):
            logger.warning(
                request,
                '(Save share settings): All additional share settings are False, but main setting is True.',
            )
            return JsonResponse(
                {
                    'status': 'fail',
                    'message': 'All additional share settings are False, but main setting is True.',
                }
            )

        # Если основной чекбокс выключен, то и все остальные должны быть выключены.
        # Если это не так - исправляем.
        if not switch_share_general and any(
            [switch_share_dashboard, switch_share_city_map, switch_share_region_map]
        ):
            switch_share_dashboard = False
            switch_share_city_map = False
            switch_share_region_map = False
            logger.warning(
                request,
                '(Save share settings): All additional share settings are True, but main setting is False.',
            )

        ShareSettings.objects.update_or_create(
            user=user,
            defaults={
                'user': user,
                'can_share': switch_share_general,
                'can_share_dashboard': switch_share_dashboard,
                'can_share_city_map': switch_share_city_map,
                'can_share_region_map': switch_share_region_map,
            },
        )
        logger.info(request, '(Save share settings): Successful saving of share settings')
        return JsonResponse({'status': 'ok'})
    else:
        logger.warning(request, '(Save share settings): Connection is not using the POST method')
        raise Http404
