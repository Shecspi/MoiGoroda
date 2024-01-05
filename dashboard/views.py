from datetime import timedelta, date, timezone

from django.db.models import Count
from django.contrib.auth.models import User
from django.db.models.functions import TruncDay, TruncDate
from django.views.generic import TemplateView

from city.models import VisitedCity


class Dashboard(TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['qty_users'] = User.objects.count()
        context['qty_registrations_yesteday'] = User.objects.filter(
            date_joined__contains=date.today() - timedelta(days=1)
        ).count()

        context['qty_registrations_week'] = User.objects.annotate(
            day=TruncDay('date_joined', tzinfo=timezone.utc)
        ).filter(
            day__range=[date.today() - timedelta(days=7), date.today()]
        ).count()

        context['qty_registrations_month'] = User.objects.annotate(
            day=TruncDay('date_joined', tzinfo=timezone.utc)
        ).filter(
            day__range=[date.today() - timedelta(days=30), date.today()]
        ).count()

        context['registrations_by_day'] = User.objects.annotate(
            day=TruncDay('date_joined', tzinfo=timezone.utc)
        ).annotate(
            date=TruncDate('day')
        ).values('date').annotate(qty=Count('id')).order_by('date')

        context['qty_visited_cities'] = VisitedCity.objects.count()
        context['average_cities'] = int(context['qty_visited_cities'] / context['qty_users'])
        # context['max_visited_cities'] = VisitedCity.objects.

        return context
