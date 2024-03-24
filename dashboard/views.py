"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import timedelta, date, timezone

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, OuterRef, Subquery
from django.contrib.auth.models import User
from django.db.models.functions import TruncDay, TruncDate
from django.shortcuts import redirect
from django.views.generic import TemplateView

from city.models import VisitedCity


class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            return redirect('main_page')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Всего пользователей
        context['qty_users'] = User.objects.count()

        # Количество регистраций вчера
        context['qty_registrations_yesteday'] = User.objects.filter(
            date_joined__contains=date.today() - timedelta(days=1)
        ).count()

        # Количество регистраций за неделю (не учитывая сегодня)
        context['qty_registrations_week'] = (
            User.objects.annotate(day=TruncDay('date_joined', tzinfo=timezone.utc))
            .filter(day__range=[date.today() - timedelta(days=7), date.today()])
            .count()
        )

        # Количество регистраций за месяц (не учитывая сегодня)
        context['qty_registrations_month'] = (
            User.objects.annotate(day=TruncDay('date_joined', tzinfo=timezone.utc))
            .filter(day__range=[date.today() - timedelta(days=30), date.today()])
            .count()
        )

        # Количество регистраций за каждый из 50 последних дней
        # Именно 50, так как график с этим количеством дней красивее всего смотрится. Субъективно
        context['registrations_by_day'] = (
            User.objects.annotate(day=TruncDay('date_joined', tzinfo=timezone.utc))
            .annotate(date=TruncDate('day'))
            .values('date')
            .annotate(qty=Count('id'))
            .order_by('-date')[:50]
        )

        # Количество посещённых городов всеми пользователями
        context['qty_visited_cities'] = VisitedCity.objects.count()

        # Среднее значение посещённых городов 1 пользователем
        context['average_cities'] = int(context['qty_visited_cities'] / context['qty_users'])

        # Максимальное количество посещённых городов 1 пользователем
        qty_visited_cities_by_user = (
            User.objects.annotate(
                qty_visited_cities=Subquery(
                    VisitedCity.objects.filter(user=OuterRef('pk'))
                    .values('user')
                    .annotate(qty=Count('pk'))
                    .values('qty')
                )
            )
            .values('username', 'qty_visited_cities')
            .exclude(qty_visited_cities=None)
            .order_by('-qty_visited_cities')
        )
        context['qty_visited_cities_by_user'] = qty_visited_cities_by_user[:50]

        # Количество пользователей без посещённых городов
        context['qty_user_without_visited_cities'] = context['qty_users'] - len(
            qty_visited_cities_by_user
        )

        context['page_title'] = 'Dashboard'
        context['page_description'] = ''

        return context
