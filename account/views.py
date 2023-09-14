import logging
import datetime

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetCompleteView, PasswordResetDoneView, \
    PasswordChangeView
from django.db.models import Count, Q, F
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView

from account.forms import SignUpForm, SignInForm, UpdateProfileForm
from region.models import Region, Area
from city.models import VisitedCity
from utils.LoggingMixin import LoggingMixin

logger_email = logging.getLogger(__name__)
logger_basic = logging.getLogger('moi-goroda')


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
        context['page_description'] = 'Зарегистрируйтесь на сервисе "Мои города" для того, чтобы сохранять свои посещённые города и просматривать их на карте'

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


class Profile_Detail(LoginRequiredMixin, LoggingMixin, DetailView):
    """
    Отображает страницу профиля пользователя.
    На этой странице отображается вся статистика пользователя,
    а также возможно изменить его данные.

    ID пользователя берётся из сессии, поэтому просмотр данных другого пользователя недоступен.

    > Доступ на эту страницу возможен только авторизованным пользователям.
    """
    model = User
    template_name = 'account/profile.html'

    def get_object(self, queryset=None):
        """
        Убирает необходимость указывать ID пользователя в URL, используя сессионный ID.
        """
        return get_object_or_404(User, pk=self.request.user.pk)

    def get(self, *args, **kwargs):
        self.set_message(self.request, 'Viewing the profile page')

        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user.pk
        logger_basic.info(f'Viewing a profile: {self.request.user.username} ({self.request.user.email})')

        # Все посещённые города
        cities = VisitedCity.objects.filter(user=user)
        cities_last = cities.order_by(F('date_of_visit').desc(nulls_last=True), 'city__title')[:5]
        cities_this_year = cities.filter(date_of_visit__year=datetime.datetime.now().year).count()
        num_cities = cities.count()

        regions = Region.objects.all().annotate(
            total_cities=Count('city', distinct=True),
            visited_cities=Count('city', filter=Q(city__visitedcity__user__id=user), distinct=True)
        ).exclude(visitedcity__city=None).exclude(~Q(visitedcity__user=user)).order_by('-visited_cities')[:10]

        areas = Area.objects.all().order_by('title').annotate(
            total_regions=Count('region', distinct=True),
            visited_regions=Count('region', filter=Q(region__visitedcity__user__id=user), distinct=True))

        context['cities'] = {
            'num_visited': num_cities,
            'last_visited': cities_last,
            'visited_this_year': cities_this_year
        }
        context['regions'] = {
            'visited': regions,
            'num_visited': Region.objects.all().exclude(
                visitedcity__city=None
            ).exclude(
                ~Q(visitedcity__user=user)
            ).count()
        }
        context['areas'] = areas

        context['active_page'] = 'profile'
        context['page_title'] = 'Профиль'
        context['page_description'] = 'Здесь отображается подробная информация о Ваших посещённых городах'

        return context


class UpdateUser(LoginRequiredMixin, UpdateView):
    """
    Обновляет данные пользователя.

    > Доступ на эту страницу возможен только авторизованным пользователям.
    """
    model = User
    form_class = UpdateProfileForm
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        logger_basic.info(f"Updating user's information: {self.request.user.username} ({self.request.user.email})")
        return super().form_valid(form)


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
