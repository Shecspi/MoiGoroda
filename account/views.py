import logging

from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import Http404, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, UpdateView, TemplateView
from django.contrib.auth.views import LoginView, PasswordResetDoneView, PasswordChangeView

from account.models import ShareSettings
from utils.LoggingMixin import LoggingMixin
from services.db.statistics.visited_city import *
from account.forms import SignUpForm, SignInForm, UpdateProfileForm
from services.db.statistics.fake_statistics import get_fake_statistics
from services.db.statistics.get_info_for_statistic_cards_and_charts import get_info_for_statistic_cards_and_charts

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
            'page_description'] = 'Зарегистрируйтесь на сервисе "Мои города" для того, чтобы сохранять свои ' \
                                  'посещённые города и просматривать их на карте'

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
        context[
            'page_description'] = 'Войдите в свой аккаунт для того, чтобы посмотреть свои посещённые города ' \
                                  'и сохранить новые'

        return context


def signup_success(request):
    return render(request, 'account/signup_success.html')


class Stats(LoginRequiredMixin, LoggingMixin, TemplateView):
    """
    Отображает страницу со статистикой пользователя.

    ID пользователя берётся из сессии, поэтому просмотр данных другого пользователя недоступен.

    > Доступ на эту страницу возможен только авторизованным пользователям.
    """
    template_name = 'account/statistics/statistics.html'

    def get(self, *args, **kwargs):
        self.set_message(
            self.request,
            f"Viewing stats: {self.request.user.username} ({self.request.user.email})"
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
                'switch_share_region_map': False
            }
        else:
            share_settings = {
                'switch_share_general': obj.can_share,
                'switch_share_basic_info': obj.can_share_dashboard,
                'switch_share_city_map': obj.can_share_city_map,
                'switch_share_region_map': obj.can_share_region_map
            }
        context['share_settings'] = share_settings

        ##################################
        # --- Вспомогательные данные --- #
        ##################################

        context['active_page'] = 'stats'
        context['page_title'] = 'Личная статистика'
        context['page_description'] = 'Здесь отображается подробная информация о результатах Ваших путешествий' \
                                      ' - посещённые города, регионы и федеральнаые округа'

        return context | get_info_for_statistic_cards_and_charts(user_id)


@login_required()
def save_share_settings(request):
    """
    Производит проверку данных, переданных из формы настроек "Поделиться статистикой" и сохраняет их в БД.
    В таблице для каждого пользователя может быть только одна запись с настройками.
    Поэтому данная функция либо обновляет эту запись, либо создаёт новую, если её ещё нет.
    """
    logger = LoggingMixin()

    if request.method == 'POST':
        user = get_object_or_404(User, pk=request.user.pk)

        share_data = request.POST.dict()
        switch_share_general = True if share_data.get('switch_share_general') else False
        switch_share_dashboard = True if share_data.get('switch_share_dashboard') else False
        switch_share_city_map = True if share_data.get('switch_share_city_map') else False
        switch_share_region_map = True if share_data.get('switch_share_region_map') else False

        # В ситуации, когда основной чекбокс включён, а все остальные выключены, возвращаем ошибку,
        # так как не понятно, как конкретно обрабатывать такую ситуацию.
        if switch_share_general and not any([switch_share_dashboard, switch_share_city_map, switch_share_region_map]):
            logger.set_message(
                request,
                '(Save share settings): All additional share settings are False, but main setting is True.'
            )
            return JsonResponse({
                'status': 'fail',
                'message': 'All additional share settings are False, but main setting is True.'
            })

        # Если основной чекбокс выключен, то и все остальные должны быть выключены.
        # Если это не так - исправляем.
        if not switch_share_general and any([switch_share_dashboard, switch_share_city_map, switch_share_region_map]):
            switch_share_dashboard = False
            switch_share_city_map = False
            switch_share_region_map = False
            logger.set_message(
                request,
                '(Save share settings): All additional share settings are True, but main setting is False.'
            )

        ShareSettings.objects.update_or_create(
            user=user,
            defaults={
                'user': user,
                'can_share': switch_share_general,
                'can_share_dashboard': switch_share_dashboard,
                'can_share_city_map': switch_share_city_map,
                'can_share_region_map': switch_share_region_map
            }
        )
        logger.set_message(
            request,
            '(Save share settings): Successful saving of share settings'
        )
        return JsonResponse({
            'status': 'ok'
        })
    else:
        logger.set_message(
            request,
            '(Save share settings): Connection is not using the POST method'
        )
        raise Http404


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
