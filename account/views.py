import datetime

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView

from account.forms import SignUpForm, SignInForm, UpdateProfileForm
from travel.models import VisitedCity, Region, Area


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
            return redirect('city-all')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = User.objects.create_user(
            username=self.request.POST['username'],
            password=self.request.POST['password1'],
            first_name=self.request.POST['first_name'],
            last_name=self.request.POST['last_name'],
            email=self.request.POST['email']
        )
        user.save()
        login(self.request, user)

        return redirect('city-all')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['breadcrumb'] = [
            {'url': 'main_page', 'title': 'Главная', 'active': False},
            {'url': '', 'title': 'Регистрация', 'active': True}
        ]

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
            return redirect('city-all')

        return super().dispatch(request, *args, **kwargs)


def signup_success(request):
    return render(request, 'account/signup_success.html')


class Profile_Detail(LoginRequiredMixin, DetailView):
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user.pk

        # Все посещённые города
        cities = VisitedCity.objects.filter(user=user)
        cities_last = cities.order_by('-date_of_visit', 'city__title')[:5]
        cities_this_year = cities.filter(date_of_visit__year=datetime.datetime.now().year).count()
        num_cities = cities.count()

        regions = Region.objects.all().order_by('title').annotate(
            total_cities=Count('city', distinct=True),
            visited_cities=Count('city', filter=Q(city__visitedcity__user__id=user), distinct=True)
        ).exclude(visitedcity__city=None).exclude(~Q(visitedcity__user=user))

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
            'num_visited': regions.count()
        }
        context['areas'] = areas

        context['breadcrumb'] = [
            {'url': 'main_page', 'title': 'Главная', 'active': False},
            {'url': '', 'title': 'Профиль', 'active': True}
        ]

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            {'url': 'main_page', 'title': 'Главная', 'active': False},
            {'url': '', 'title': 'Профиль', 'active': True}
        ]

        return context
