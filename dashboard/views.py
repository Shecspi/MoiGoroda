from datetime import timedelta, date, timezone

from django.db.models import Count, F
from django.contrib.auth.models import User
from django.db.models.functions import TruncDay, TruncDate
from django.views.generic import TemplateView

from city.models import VisitedCity


class Dashboard(TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Всего пользователей
        context['qty_users'] = User.objects.count()

        # Количество регистраций вчера
        context['qty_registrations_yesteday'] = User.objects.filter(
            date_joined__contains=date.today() - timedelta(days=1)
        ).count()

        # Количество регистраций за неделю (не учитывая сегодня)
        context['qty_registrations_week'] = User.objects.annotate(
            day=TruncDay('date_joined', tzinfo=timezone.utc)
        ).filter(
            day__range=[date.today() - timedelta(days=7), date.today()]
        ).count()

        # Количество регистраций за месяц (не учитывая сегодня)
        context['qty_registrations_month'] = User.objects.annotate(
            day=TruncDay('date_joined', tzinfo=timezone.utc)
        ).filter(
            day__range=[date.today() - timedelta(days=30), date.today()]
        ).count()

        # Количество регистраций за каждый из 50 последних дней
        # Именно 50, так как график с этим количеством дней красивее всего смотрится. Субъективно
        context['registrations_by_day'] = User.objects.annotate(
            day=TruncDay('date_joined', tzinfo=timezone.utc)
        ).annotate(
            date=TruncDate('day')
        ).values('date').annotate(qty=Count('id')).order_by('-date')[:50]

        # Количество посещённых городов всеми пользователями
        context['qty_visited_cities'] = VisitedCity.objects.count()

        # Среднее значение посещённых городов 1 пользователем
        context['average_cities'] = int(context['qty_visited_cities'] / context['qty_users'])

        # Максимальное количество посещённых городов 1 пользователем
        # context['max_visited_cities'] = User.objects.annotate(
        #     qty_visited_cities=VisitedCity.objects.filter(user=F('pk')).count()
        # ).order_by('-qty_visited_cities')[0]

        return context
