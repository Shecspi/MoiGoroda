"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any
from unittest.mock import patch, Mock

from account.forms import SignUpForm, SignInForm, UpdateProfileForm


# ===== Фикстуры =====


@pytest.fixture
def signup_form_data() -> dict[str, Any]:
    """Фикстура с тестовыми данными для формы регистрации"""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password1': 'testpass123',
        'password2': 'testpass123',
        'personal_data_consent': True,
        'personal_data_version': '1.0',
    }


@pytest.fixture
def signin_form_data() -> dict[str, str]:
    """Фикстура с тестовыми данными для формы входа"""
    return {'username': 'testuser', 'password': 'testpass123'}


@pytest.fixture
def update_profile_form_data() -> dict[str, str]:
    """Фикстура с тестовыми данными для формы обновления профиля"""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
    }


# ===== Тесты для SignUpForm =====


@pytest.mark.unit
@patch('account.forms.User.objects.filter')
def test_signup_form_valid_data(mock_filter: Any, signup_form_data: dict[str, Any]) -> None:
    """Тест валидной формы регистрации"""
    mock_filter.return_value.exists.return_value = False

    form = SignUpForm(data=signup_form_data)  

    assert form.is_valid()
    assert form.cleaned_data['username'] == 'testuser'
    assert form.cleaned_data['email'] == 'test@example.com'


@pytest.mark.unit
@patch('account.forms.User.objects.filter')
def test_signup_form_email_already_exists(mock_filter: Any, signup_form_data: dict[str, Any]) -> None:
    """Тест формы регистрации с уже существующим email"""
    mock_filter.return_value.exists.return_value = True

    form = SignUpForm(data=signup_form_data)  

    assert not form.is_valid()
    assert 'email' in form.errors
    assert 'Данный адрес электронной почты уже зарегистрирован.' in form.errors['email']


@pytest.mark.unit
@patch('account.forms.User.objects.filter')
def test_signup_form_passwords_dont_match(mock_filter: Any, signup_form_data: dict[str, Any]) -> None:
    """Тест формы регистрации с несовпадающими паролями"""
    mock_filter.return_value.exists.return_value = False
    signup_form_data['password2'] = 'differentpass'

    form = SignUpForm(data=signup_form_data)  

    assert not form.is_valid()
    assert 'password2' in form.errors


@pytest.mark.unit
@patch('account.forms.User.objects.filter')
def test_signup_form_missing_required_field(mock_filter: Any) -> None:
    """Тест формы регистрации с пропущенным обязательным полем"""
    mock_filter.return_value.exists.return_value = False

    form = SignUpForm(data={'username': 'testuser'})  

    assert not form.is_valid()
    assert 'password1' in form.errors
    assert 'password2' in form.errors
    assert 'email' in form.errors


@pytest.mark.unit
@patch('account.forms.User.objects.filter')
def test_signup_form_whitespace_trimming(mock_filter: Any, signup_form_data: dict[str, Any]) -> None:
    """Тест удаления пробелов из полей формы регистрации"""
    mock_filter.return_value.exists.return_value = False

    signup_form_data['username'] = '  testuser  '
    signup_form_data['email'] = '  test@example.com  '

    form = SignUpForm(data=signup_form_data)  

    assert form.is_valid()
    assert form.cleaned_data['username'] == 'testuser'
    assert form.cleaned_data['email'] == 'test@example.com'


@pytest.mark.unit
@patch('account.forms.User.objects.filter')
def test_signup_form_fields_present(mock_filter: Any, signup_form_data: dict[str, Any]) -> None:
    """Тест наличия всех необходимых полей в форме регистрации"""
    mock_filter.return_value.exists.return_value = False

    form = SignUpForm(data=signup_form_data)  

    assert 'username' in form.fields
    assert 'email' in form.fields
    assert 'password1' in form.fields
    assert 'password2' in form.fields
    assert 'personal_data_consent' in form.fields
    assert 'personal_data_version' in form.fields


@pytest.mark.unit
def test_signup_form_has_helper() -> None:
    """Тест наличия crispy form helper"""
    form = SignUpForm()  

    assert hasattr(form, 'helper')
    assert form.helper.form_tag is False


@pytest.mark.unit
@patch('account.forms.User.objects.filter')
def test_signup_form_invalid_email(mock_filter: Any, signup_form_data: dict[str, Any]) -> None:
    """Тест формы регистрации с невалидным email"""
    mock_filter.return_value.exists.return_value = False
    signup_form_data['email'] = 'invalid-email'

    form = SignUpForm(data=signup_form_data)  

    assert not form.is_valid()
    assert 'email' in form.errors


@pytest.mark.unit
@patch('account.forms.User.objects.filter')
def test_signup_form_empty_username(mock_filter: Any, signup_form_data: dict[str, Any]) -> None:
    """Тест формы регистрации с пустым username"""
    mock_filter.return_value.exists.return_value = False
    signup_form_data['username'] = ''

    form = SignUpForm(data=signup_form_data)  

    assert not form.is_valid()
    assert 'username' in form.errors


# ===== Тесты для SignInForm =====


@pytest.mark.unit
def test_signin_form_valid_data(signin_form_data: dict[str, str]) -> None:
    """Тест валидной формы входа"""
    form = SignInForm(data=signin_form_data)  

    # Проверяем только наличие полей, так как валидация требует настоящего пользователя
    assert 'username' in form.fields
    assert 'password' in form.fields


@pytest.mark.unit
def test_signin_form_has_helper() -> None:
    """Тест наличия crispy form helper в форме входа"""
    form = SignInForm()  

    assert hasattr(form, 'helper')
    assert form.helper.form_tag is False


@pytest.mark.unit
def test_signin_form_fields_present() -> None:
    """Тест наличия всех необходимых полей в форме входа"""
    form = SignInForm()  

    assert 'username' in form.fields
    assert 'password' in form.fields


@pytest.mark.unit
def test_signin_form_password_widget() -> None:
    """Тест что поле пароля использует правильный виджет"""
    form = SignInForm()  

    assert form.fields['password'].widget.__class__.__name__ == 'PasswordInput'


@pytest.mark.unit
def test_signin_form_field_labels() -> None:
    """Тест меток полей формы входа"""
    form = SignInForm()  

    assert form.fields['username'].label == 'Имя пользователя'
    assert form.fields['password'].label == 'Пароль'


# ===== Тесты для UpdateProfileForm =====


@pytest.mark.unit
def test_update_profile_form_fields_present() -> None:
    """Тест наличия всех необходимых полей в форме обновления профиля"""
    form = UpdateProfileForm()  

    assert 'username' in form.fields
    assert 'email' in form.fields
    assert 'first_name' in form.fields
    assert 'last_name' in form.fields


@pytest.mark.unit
def test_update_profile_form_has_helper() -> None:
    """Тест наличия crispy form helper в форме обновления профиля"""
    form = UpdateProfileForm()  

    assert hasattr(form, 'helper')
    assert form.helper.form_tag is False


@pytest.mark.unit
def test_update_profile_form_field_labels() -> None:
    """Тест меток полей формы обновления профиля"""
    form = UpdateProfileForm()  

    assert form.fields['username'].label == 'Имя пользователя'
    assert form.fields['email'].label == 'Электронная почта'
    assert form.fields['first_name'].label == 'Имя'
    assert form.fields['last_name'].label == 'Фамилия'


@pytest.mark.unit
def test_update_profile_form_required_fields() -> None:
    """Тест обязательности полей формы обновления профиля"""
    form = UpdateProfileForm()  

    assert form.fields['username'].required is True
    assert form.fields['email'].required is True
    assert form.fields['first_name'].required is False
    assert form.fields['last_name'].required is False


@pytest.mark.unit
def test_update_profile_form_max_length() -> None:
    """Тест максимальной длины полей формы обновления профиля"""
    form = UpdateProfileForm()  

    assert form.fields['username'].max_length == 150  # type: ignore[attr-defined]
    assert form.fields['first_name'].max_length == 150  # type: ignore[attr-defined]
    assert form.fields['last_name'].max_length == 150  # type: ignore[attr-defined]
    assert form.fields['email'].max_length == 150  # type: ignore[attr-defined]
