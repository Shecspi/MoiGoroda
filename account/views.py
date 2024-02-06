import logging
import datetime

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetCompleteView, PasswordResetDoneView, \
    PasswordChangeView
from django.db.models import Count, Q, F, FloatField
from django.db.models.functions import Cast, TruncMonth, TruncYear
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView, FormView

from account.forms import SignUpForm, SignInForm, UpdateProfileForm
from region.models import Region, Area
from city.models import VisitedCity, City
from services.db.visited_city import get_number_of_visited_cities, get_number_of_visited_cities_by_year, \
    get_number_of_not_visited_cities, calculate_ratio, get_last_10_visited_cities
from utils.LoggingMixin import LoggingMixin

logger_email = logging.getLogger(__name__)


class SignUp(CreateView):
    """
    Отображает и обрабатывает форму регистрации.

    > Авторизованных пользователей перенаправляет в список посещённых городов.
    """
    form_class = SignUpForm
    success_url = reverse_lazy('signup_success')
    template_name = 'account/signup.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('city-all-list')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = User.objects.create_user(
            username=self.request.POST['username'],
            password=self.request.POST['password1'],
            email=self.request.POST['email']
        )
        user.save()
        logger_email.info(
            f"Registration of a new user: {self.request.POST['username']} ({self.request.POST['email']}). "
            f"Total numbers of users: {User.objects.count()}")
        login(self.request, user)

        return redirect('city-all-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['page_title'] = 'Регистрация'
        context[
            'page_description'] = 'Зарегистрируйтесь на сервисе "Мои города" для того, чтобы сохранять свои посещённые города и просматривать их на карте'

        return context


class SignIn(LoginView):
    """
    Отображает и обрабатывает форму авторизации.

    > Авторизованных пользователей перенаправляет в список посещённых городов.
    """
    form_class = SignInForm
    template_name = 'account/signin.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('city-all-list')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['page_title'] = 'Вход'
        context['page_description'] = 'Войдите в свой аккаунт для того, чтобы посмотреть свои посещённые города и сохранить новые'

        return context


def signup_success(request):
    return render(request, 'account/signup_success.html')


class Stats(LoginRequiredMixin, LoggingMixin, TemplateView):
    """
    Отображает страницу со статистикой пользователя.

    ID пользователя берётся из сессии, поэтому просмотр данных другого пользователя недоступен.

    > Доступ на эту страницу возможен только авторизованным пользователям.
    """
    template_name = 'account/stats.html'

    def get(self, *args, **kwargs):
        self.set_message(
            self.request,
            f"Viewing stats: {self.request.user.username} ({self.request.user.email})"
        )

        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user.pk
        user_id = self.request.user.pk

        # Статистика по городам
        visited_cities = VisitedCity.objects.filter(user=user)
        last_cities = visited_cities.order_by(F('date_of_visit').desc(nulls_last=True), 'city__title')[:10]

        num_cities_this_year = visited_cities.filter(date_of_visit__year=datetime.datetime.now().year).count()
        num_cities_prev_year = visited_cities.filter(date_of_visit__year=datetime.datetime.now().year - 1).count()
        num_cities_2_year = num_cities_prev_year + num_cities_this_year
        ratio_cities_this_year = calculate_ratio(num_cities_this_year, num_cities_2_year)
        ratio_cities_prev_year = 100 - ratio_cities_this_year

        num_visited_cities = visited_cities.count()
        num_all_cities = City.objects.count()
        num_not_visited_cities = num_all_cities - num_visited_cities

        qty_cities_by_year = (
            visited_cities
            .annotate(year=TruncYear('date_of_visit'))
            .values('year')
            .exclude(year=None)
            .annotate(qty=Count('id', distinct=True))
            .values('year', 'qty')
        )
        qty_cities_by_month = (
            visited_cities
            .annotate(month_year=TruncMonth('date_of_visit'))
            .values('month_year')
            .order_by('-month_year')
            .exclude(month_year=None)
            .annotate(qty=Count('id', distinct=True))
            .values('month_year', 'qty')
        )[:24]

        # Статистика по регионам
        regions = (
            Region.objects
            .all()
            .annotate(
                # Добавляем в QuerySet общее количество городов в регионе
                total_cities=Count('city', distinct=True),
                # Добавляем в QuerySet количество посещённых городов в регионе
                visited_cities=Count('city', filter=Q(city__visitedcity__user__id=user), distinct=True),
                # Добавляем в QuerySet процентное отношение посещённых городов
                # Без Cast(..., output_field=...) деление F() на F() выдаёт int, то есть очень сильно теряется точность.
                # Например, 76 / 54 получается 1.
                ratio_visited=(
                                      Cast(
                                          F('visited_cities'), output_field=FloatField()
                                      ) / Cast(
                                  F('total_cities'), output_field=FloatField()
                              )) * 100)
            .exclude(visitedcity__city=None)
            .exclude(~Q(visitedcity__user=user))
            .order_by('-ratio_visited', '-visited_cities')
        )
        num_visited_regions = (
            Region.objects
            .all()
            .exclude(visitedcity__city=None)
            .exclude(~Q(visitedcity__user=user))
            .count()
        )
        num_not_visited_regions = Region.objects.count() - num_visited_regions
        # Количество регионов, в которых посещены все города.
        # Для этого забираем те записи, где 'total_cities' и 'visitied_cities' равны.
        num_finished_regions = regions.filter(total_cities=F('visited_cities')).count()

        ratio_visited = calculate_ratio(num_visited_regions, num_visited_regions + num_not_visited_regions)
        ratio_not_visited = 100 - ratio_visited
        ratio_finished = calculate_ratio(num_finished_regions, num_finished_regions + num_not_visited_regions)
        ratio_not_finished = 100 - ratio_finished

        areas = (
            Area.objects
            .all()
            .annotate(
                # Добавляем в QuerySet общее количество регионов в округе
                total_regions=Count('region', distinct=True),
                # Добавляем в QuerySet количество посещённых регионов в округе
                visited_regions=Count('region', filter=Q(region__visitedcity__user__id=user), distinct=True),
                # Добавляем в QuerySet процентное соотношение посещённых регионов.
                # Без Cast(..., output_field=...) деление F() на F() выдаёт int, то есть очень сильно теряется точность.
                # Например, 76 / 54 получается 1.
                ratio_visited=(
                    Cast(
                        F('visited_regions'), output_field=FloatField()
                    ) / Cast(
                        F('total_regions'), output_field=FloatField()
                    )) * 100)
            .order_by('-ratio_visited', 'title')
        )

        ###################################################

        ratio_visited_cities = calculate_ratio(num_visited_cities, num_all_cities)
        ratio_not_visited_cities = 100 - ratio_visited_cities
        
        context['cities'] = {
            'number_of_visited_cities': get_number_of_visited_cities(user_id),
            'number_of_not_visited_cities': get_number_of_not_visited_cities(user_id),
            'ratio_visited': ratio_visited_cities,
            'ratio_not_visited': ratio_not_visited_cities,
            'last_visited': get_last_10_visited_cities(user_id),
            'number_of_visited_cities_current_year': get_number_of_visited_cities_by_year(
                self.request.user.pk,
                datetime.datetime.now().year
            ),
            'number_of_visited_cities_previoous_year': get_number_of_visited_cities_by_year(
                self.request.user.pk,
                datetime.datetime.now().year - 1
            ),
            'ratio_this_year': ratio_cities_this_year,
            'ratio_prev_year': ratio_cities_prev_year,
            'qty_cities_by_year': qty_cities_by_year,
            'qty_cities_by_month': qty_cities_by_month
        }
        context['regions'] = {
            'visited': regions[:10],
            'num_visited': num_visited_regions,
            'num_not_visited': num_not_visited_regions,
            'num_finished': num_finished_regions,
            'ratio_visited': ratio_visited,
            'ratio_not_visited': ratio_not_visited,
            'ratio_finished': ratio_finished,
            'ratio_not_finished': ratio_not_finished
        }
        context['areas'] = areas

        context['active_page'] = 'stats'
        context['page_title'] = 'Личная статистика'
        context['page_description'] = 'Здесь отображается подробная информация о результатах Ваших путешествий' \
                                      ' - посещённые города, регионы и федеральнаые округа'

        return context


class Profile(LoginRequiredMixin, LoggingMixin, UpdateView):
    form_class = UpdateProfileForm
    success_url = reverse_lazy('profile')
    template_name = 'account/profile.html'

    def get_object(self, queryset=None):
        """
        Убирает необходимость указывать ID пользователя в URL, используя сессионный ID.
        """
        return get_object_or_404(User, pk=self.request.user.pk)

    def form_valid(self, form):
        """
        Переопределение этого метода нужно только для того, чтобы произвести запись в лог.
        """
        self.set_message(
            self.request,
            f"Updating user's information: {self.request.user.username} ({self.request.user.email})"
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['active_page'] = 'profile'
        context['page_title'] = 'Профиль'
        context['page_description'] = 'Просмотр и изменения персональной информации'

        return context


class MyPasswordChangeView(PasswordChangeView):
    template_name = 'account/profile__password_change_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['page_title'] = 'Изменение пароля'
        context['page_description'] = 'Для того, чтобы изменить свой пароль, введите старый и новый пароли'

        return context


class MyPasswordResetDoneView(LoginRequiredMixin, PasswordResetDoneView):
    template_name = 'account/profile__password_change_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['page_title'] = 'Изменение пароля'
        context['page_description'] = 'Пароль успешно изменён'

        return context
