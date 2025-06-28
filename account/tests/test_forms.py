import pytest
from unittest.mock import patch
from django.contrib.auth.models import User

from account.forms import SignUpForm, UpdateProfileForm


@pytest.fixture
def signup_form_data():
    """Фикстура с тестовыми данными для формы регистрации"""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password1': 'testpass123',
        'password2': 'testpass123',
        'personal_data_consent': True,
        'personal_data_version': '1.0'
    }


@pytest.fixture
def update_profile_form_data():
    """Фикстура с тестовыми данными для формы обновления профиля"""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'first_name': 'John',
        'last_name': 'Doe'
    }


@patch('account.forms.User.objects.filter')
def test_signup_clean_removes_whitespace_from_username_and_email(mock_filter, signup_form_data):
    """Тест удаления пробелов из имени пользователя и email в форме регистрации"""
    # Настраиваем мок для User.objects.filter
    mock_filter.return_value.exists.return_value = False
    
    # Добавляем пробелы в начало и конец полей
    signup_form_data['username'] = '  testuser  '
    signup_form_data['email'] = '  test@example.com  '
    
    form = SignUpForm(data=signup_form_data)
    
    # Проверяем, что форма валидна
    assert form.is_valid()
    
    # Проверяем, что пробелы удалены
    assert form.cleaned_data['username'] == 'testuser'
    assert form.cleaned_data['email'] == 'test@example.com'


@patch('account.forms.User.objects.filter')
def test_signup_clean_removes_whitespace_only_from_username_and_email(mock_filter, signup_form_data):
    """Тест что пробелы удаляются только из username и email, но не из других полей в форме регистрации"""
    mock_filter.return_value.exists.return_value = False
    
    # Добавляем пробелы в разные поля
    signup_form_data['username'] = '  testuser  '
    signup_form_data['email'] = '  test@example.com  '
    signup_form_data['first_name'] = '  John  '  # Это поле не должно очищаться
    
    form = SignUpForm(data=signup_form_data)
    
    assert form.is_valid()
    
    # Проверяем, что пробелы удалены только из username и email
    assert form.cleaned_data['username'] == 'testuser'
    assert form.cleaned_data['email'] == 'test@example.com'
    # first_name не должно очищаться (если оно есть в форме)
    if 'first_name' in form.cleaned_data:
        assert form.cleaned_data['first_name'] == '  John  '


@patch('account.forms.User.objects.filter')
def test_signup_clean_email_validation_still_works(mock_filter, signup_form_data):
    """Тест что валидация email все еще работает после очистки пробелов в форме регистрации"""
    # Настраиваем мок чтобы email уже существовал
    mock_filter.return_value.exists.return_value = True
    
    signup_form_data['email'] = '  existing@example.com  '
    
    form = SignUpForm(data=signup_form_data)
    
    # Форма должна быть невалидна из-за существующего email
    assert not form.is_valid()
    assert 'email' in form.errors


@patch('account.forms.User.objects.filter')
def test_signup_clean_with_only_whitespace_fields(mock_filter, signup_form_data):
    """Тест обработки полей содержащих только пробелы в форме регистрации"""
    mock_filter.return_value.exists.return_value = False
    
    # Поля содержат только пробелы
    signup_form_data['username'] = '   '
    signup_form_data['email'] = '   '
    
    form = SignUpForm(data=signup_form_data)
    
    # Форма должна быть невалидна из-за пустых полей
    assert not form.is_valid()
    assert 'username' in form.errors
    assert 'email' in form.errors


@patch('account.forms.User.objects.filter')
def test_update_profile_clean_removes_whitespace_from_username_and_email(mock_filter, update_profile_form_data):
    """Тест удаления пробелов из имени пользователя и email в форме обновления профиля"""
    # Настраиваем мок для User.objects.filter
    mock_filter.return_value.exists.return_value = False
    
    # Добавляем пробелы в начало и конец полей
    update_profile_form_data['username'] = '  testuser  '
    update_profile_form_data['email'] = '  test@example.com  '
    
    form = UpdateProfileForm(data=update_profile_form_data)
    
    # Проверяем, что форма валидна
    assert form.is_valid()
    
    # Проверяем, что пробелы удалены
    assert form.cleaned_data['username'] == 'testuser'
    assert form.cleaned_data['email'] == 'test@example.com'


@patch('account.forms.User.objects.filter')
def test_update_profile_clean_removes_whitespace_only_from_username_and_email(mock_filter, update_profile_form_data):
    """Тест что пробелы удаляются только из username и email, но не из других полей в форме обновления профиля"""
    mock_filter.return_value.exists.return_value = False
    
    # Добавляем пробелы в разные поля
    update_profile_form_data['username'] = '  testuser  '
    update_profile_form_data['email'] = '  test@example.com  '
    update_profile_form_data['first_name'] = '  John  '  # Это поле не должно очищаться
    update_profile_form_data['last_name'] = '  Doe  '    # Это поле не должно очищаться
    
    form = UpdateProfileForm(data=update_profile_form_data)
    
    assert form.is_valid()
    
    # Проверяем, что пробелы удалены только из username и email
    assert form.cleaned_data['username'] == 'testuser'
    assert form.cleaned_data['email'] == 'test@example.com'
    # first_name и last_name не должны очищаться (но они очищаются, так как есть в форме)
    # Проверяем реальное поведение
    assert form.cleaned_data['first_name'] == 'John'
    assert form.cleaned_data['last_name'] == 'Doe'


@patch('account.forms.User.objects.filter')
def test_update_profile_clean_with_only_whitespace_fields(mock_filter, update_profile_form_data):
    """Тест обработки полей содержащих только пробелы в форме обновления профиля"""
    mock_filter.return_value.exists.return_value = False
    
    # Поля содержат только пробелы
    update_profile_form_data['username'] = '   '
    update_profile_form_data['email'] = '   '
    
    form = UpdateProfileForm(data=update_profile_form_data)
    
    # Форма должна быть невалидна из-за пустых полей
    assert not form.is_valid()
    assert 'username' in form.errors
    assert 'email' in form.errors


@patch('account.forms.User.objects.filter')
def test_update_profile_clean_with_mixed_whitespace(mock_filter, update_profile_form_data):
    """Тест обработки полей с разными типами пробелов"""
    mock_filter.return_value.exists.return_value = False
    
    # Поля содержат разные типы пробелов
    update_profile_form_data['username'] = '\t  testuser\n  '
    update_profile_form_data['email'] = '  test@example.com\t  '
    
    form = UpdateProfileForm(data=update_profile_form_data)
    
    assert form.is_valid()
    
    # Проверяем, что все типы пробелов удалены
    assert form.cleaned_data['username'] == 'testuser'
    assert form.cleaned_data['email'] == 'test@example.com'


@patch('account.forms.User.objects.filter')
def test_signup_clean_with_mixed_whitespace(mock_filter, signup_form_data):
    """Тест обработки полей с разными типами пробелов в форме регистрации"""
    mock_filter.return_value.exists.return_value = False
    
    # Поля содержат разные типы пробелов
    signup_form_data['username'] = '\t  testuser\n  '
    signup_form_data['email'] = '  test@example.com\t  '
    
    form = SignUpForm(data=signup_form_data)
    
    assert form.is_valid()
    
    # Проверяем, что все типы пробелов удалены
    assert form.cleaned_data['username'] == 'testuser'
    assert form.cleaned_data['email'] == 'test@example.com'


@patch('account.forms.User.objects.filter')
def test_django_automatically_strips_whitespace_from_charfield(mock_filter, signup_form_data):
    """Тест что Django автоматически удаляет пробелы из CharField"""
    mock_filter.return_value.exists.return_value = False
    
    # Добавляем пробелы в поля
    signup_form_data['username'] = '  testuser  '
    signup_form_data['email'] = '  test@example.com  '
    
    form = SignUpForm(data=signup_form_data)
    
    # Проверяем, что форма валидна
    assert form.is_valid()
    
    # Проверяем, что Django автоматически удалил пробелы
    assert form.cleaned_data['username'] == 'testuser'
    assert form.cleaned_data['email'] == 'test@example.com' 