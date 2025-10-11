"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from django.contrib.auth.models import User

from account.models import ShareSettings, UserConsent


@pytest.mark.integration
@pytest.mark.django_db
def test_share_settings_str_method(django_user_model):
    """Тест строкового представления модели ShareSettings"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    share_settings = ShareSettings.objects.create(user=user)

    expected = 'Параметры публикации статистики пользователя testuser'
    assert str(share_settings) == expected


@pytest.mark.integration
@pytest.mark.django_db
def test_share_settings_get_absolute_url(django_user_model):
    """Тест метода get_absolute_url модели ShareSettings"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    share_settings = ShareSettings.objects.create(user=user)

    expected_url = f'/share/{share_settings.pk}/'
    assert share_settings.get_absolute_url() == expected_url


@pytest.mark.integration
@pytest.mark.django_db
def test_share_settings_create_with_all_flags_true(django_user_model):
    """Тест создания ShareSettings со всеми флагами True"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    share_settings = ShareSettings.objects.create(
        user=user,
        can_share=True,
        can_share_dashboard=True,
        can_share_city_map=True,
        can_share_region_map=True,
        can_subscribe=True,
    )

    assert share_settings.can_share is True
    assert share_settings.can_share_dashboard is True
    assert share_settings.can_share_city_map is True
    assert share_settings.can_share_region_map is True
    assert share_settings.can_subscribe is True


@pytest.mark.integration
@pytest.mark.django_db
def test_share_settings_update(django_user_model):
    """Тест обновления ShareSettings"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    share_settings = ShareSettings.objects.create(
        user=user,
        can_share=False,
        can_share_dashboard=False,
    )

    # Обновляем
    share_settings.can_share = True
    share_settings.can_share_dashboard = True
    share_settings.save()

    # Проверяем
    share_settings.refresh_from_db()
    assert share_settings.can_share is True
    assert share_settings.can_share_dashboard is True


@pytest.mark.integration
@pytest.mark.django_db
def test_user_consent_create(django_user_model):
    """Тест создания UserConsent"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    user_consent = UserConsent.objects.create(
        user=user,
        consent_given=True,
        policy_version='1.0',
        ip_address='192.168.1.1',
    )

    assert user_consent.user == user
    assert user_consent.consent_given is True
    assert user_consent.policy_version == '1.0'
    assert user_consent.ip_address == '192.168.1.1'
    assert user_consent.consent_timestamp is not None


@pytest.mark.integration
@pytest.mark.django_db
def test_user_consent_with_false_consent(django_user_model):
    """Тест создания UserConsent с согласием False"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    user_consent = UserConsent.objects.create(
        user=user,
        consent_given=False,
        policy_version='1.0',
    )

    assert user_consent.consent_given is False


@pytest.mark.integration
@pytest.mark.django_db
def test_share_settings_one_per_user(django_user_model):
    """Тест что для каждого пользователя может быть только одна запись ShareSettings"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    ShareSettings.objects.create(user=user, can_share=True)

    # Проверяем, что есть только одна запись
    assert ShareSettings.objects.filter(user=user).count() == 1

    # Обновляем через update_or_create
    ShareSettings.objects.update_or_create(
        user=user, defaults={'can_share': False, 'can_share_dashboard': True}
    )

    # Проверяем, что всё ещё одна запись
    assert ShareSettings.objects.filter(user=user).count() == 1

    # Проверяем обновлённые значения
    settings = ShareSettings.objects.get(user=user)
    assert settings.can_share is False
    assert settings.can_share_dashboard is True


@pytest.mark.integration
@pytest.mark.django_db
def test_multiple_user_consents_for_user(django_user_model):
    """Тест что для пользователя может быть несколько UserConsent (история изменений)"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    # Создаём несколько согласий
    UserConsent.objects.create(user=user, policy_version='1.0', consent_given=True)
    UserConsent.objects.create(user=user, policy_version='1.1', consent_given=True)

    # Проверяем, что есть две записи
    assert UserConsent.objects.filter(user=user).count() == 2


@pytest.mark.integration
@pytest.mark.django_db
def test_share_settings_cascade_delete(django_user_model):
    """Тест что при удалении пользователя удаляются и его ShareSettings"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    ShareSettings.objects.create(user=user, can_share=True)

    user_id = user.id
    user.delete()

    # Проверяем, что ShareSettings тоже удалились
    assert not ShareSettings.objects.filter(user_id=user_id).exists()


@pytest.mark.integration
@pytest.mark.django_db
def test_user_consent_cascade_delete(django_user_model):
    """Тест что при удалении пользователя удаляются и его UserConsent"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    UserConsent.objects.create(user=user, policy_version='1.0')

    user_id = user.id
    user.delete()

    # Проверяем, что UserConsent тоже удалились
    assert not UserConsent.objects.filter(user_id=user_id).exists()
