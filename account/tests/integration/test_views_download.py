"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import json
import openpyxl
import pytest
from io import BytesIO
from django.urls import reverse
from unittest.mock import patch, Mock


# ===== Фикстуры =====


@pytest.fixture
def create_test_user(django_user_model):
    """Создаёт тестового пользователя"""
    return django_user_model.objects.create_user(
        username='testuser', email='test@example.com', password='password123'
    )


@pytest.fixture
def mock_city_report():
    """Мокаем отчёт с городами"""
    return [
        ('Город', 'Регион', 'Дата посещения', 'Наличие сувенира', 'Оценка'),
        ('Москва', 'Москва', '2024-01-01', '+', '5'),
        ('Жуков', 'Калужская область', '2024-02-01', '-', ''),
    ]


# ===== Тесты для download view =====


@pytest.mark.integration
@pytest.mark.django_db
def test_download_view_get_request_not_allowed(client, create_test_user):
    """Тест что GET запрос на download не разрешён"""
    client.force_login(create_test_user)

    response = client.get(reverse('download'))

    assert response.status_code == 405  # Method Not Allowed


@pytest.mark.integration
@pytest.mark.django_db
def test_download_view_unauthenticated(client):
    """Тест что неавторизованный пользователь перенаправляется"""
    response = client.post(reverse('download'))

    assert response.status_code == 302
    assert response.url.startswith('/account/signin')


@pytest.mark.integration
@pytest.mark.django_db
@patch('account.views.download.CityReport')
@patch('account.views.download.logger')
def test_download_view_txt_format(mock_logger, mock_report_class, client, create_test_user):
    """Тест скачивания отчёта в формате TXT"""
    client.force_login(create_test_user)

    # Мокаем CityReport
    mock_report = Mock()
    mock_report.get_report.return_value = [
        ('Город', 'Регион', 'Дата посещения', 'Наличие сувенира', 'Оценка'),
        ('Москва', 'Москва', '2024-01-01', '+', '5'),
    ]
    mock_report_class.return_value = mock_report

    data = {'reporttype': 'city', 'filetype': 'txt'}

    response = client.post(reverse('download'), data=data)

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/txt'
    assert 'Content-Disposition' in response
    assert 'attachment' in response['Content-Disposition']
    assert '.txt' in response['Content-Disposition']
    assert 'Москва' in response.content.decode()

    mock_logger.info.assert_called()


@pytest.mark.integration
@pytest.mark.django_db
@patch('account.views.download.CityReport')
@patch('account.views.download.logger')
def test_download_view_csv_format(mock_logger, mock_report_class, client, create_test_user):
    """Тест скачивания отчёта в формате CSV"""
    client.force_login(create_test_user)

    # Мокаем CityReport
    mock_report = Mock()
    mock_report.get_report.return_value = [
        ('Город', 'Регион', 'Дата посещения', 'Наличие сувенира', 'Оценка'),
        ('Москва', 'Москва', '2024-01-01', '+', '5'),
    ]
    mock_report_class.return_value = mock_report

    data = {'reporttype': 'city', 'filetype': 'csv'}

    response = client.post(reverse('download'), data=data)

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/csv'
    assert '.csv' in response['Content-Disposition']

    content = response.content.decode()
    assert 'Город,Регион,Дата посещения,Наличие сувенира,Оценка' in content
    assert 'Москва,Москва,2024-01-01,+,5' in content


@pytest.mark.integration
@pytest.mark.django_db
@patch('account.views.download.CityReport')
@patch('account.views.download.logger')
def test_download_view_json_format(mock_logger, mock_report_class, client, create_test_user):
    """Тест скачивания отчёта в формате JSON"""
    client.force_login(create_test_user)

    # Мокаем CityReport
    mock_report = Mock()
    mock_report.get_report.return_value = [
        ('Город', 'Регион'),
        ('Москва', 'Москва'),
    ]
    mock_report_class.return_value = mock_report

    data = {'reporttype': 'city', 'filetype': 'json'}

    response = client.post(reverse('download'), data=data)

    assert response.status_code == 200
    assert response['Content-Type'] == 'application/json'
    assert '.json' in response['Content-Disposition']

    content = response.content.decode()
    parsed = json.loads(content)
    assert isinstance(parsed, list)
    assert len(parsed) == 2


@pytest.mark.integration
@pytest.mark.django_db
@patch('account.views.download.CityReport')
@patch('account.views.download.logger')
def test_download_view_xls_format(mock_logger, mock_report_class, client, create_test_user):
    """Тест скачивания отчёта в формате XLS"""
    client.force_login(create_test_user)

    # Мокаем CityReport
    mock_report = Mock()
    mock_report.get_report.return_value = [
        ('Город', 'Регион'),
        ('Москва', 'Москва'),
    ]
    mock_report_class.return_value = mock_report

    data = {'reporttype': 'city', 'filetype': 'xls'}

    response = client.post(reverse('download'), data=data)

    assert response.status_code == 200
    assert response['Content-Type'] == 'application/vnd.ms-excel'
    assert '.xls' in response['Content-Disposition']

    # Проверяем, что это валидный Excel файл
    workbook = openpyxl.load_workbook(BytesIO(response.content))
    worksheet = workbook.active
    assert worksheet['A1'].value == 'Город'
    assert worksheet['B1'].value == 'Регион'
    assert worksheet['A2'].value == 'Москва'


@pytest.mark.integration
@pytest.mark.django_db
@patch('account.views.download.logger')
def test_download_view_invalid_reporttype(mock_logger, client, create_test_user):
    """Тест скачивания с невалидным типом отчёта"""
    client.force_login(create_test_user)

    data = {'reporttype': 'invalid', 'filetype': 'txt'}

    response = client.post(reverse('download'), data=data)
    assert response.status_code == 404

    # Проверяем логирование
    assert mock_logger.info.called


@pytest.mark.integration
@pytest.mark.django_db
@patch('account.views.download.CityReport')
@patch('account.views.download.logger')
def test_download_view_invalid_filetype(mock_logger, mock_report_class, client, create_test_user):
    """Тест скачивания с невалидным типом файла"""
    client.force_login(create_test_user)

    # Мокаем CityReport
    mock_report = Mock()
    mock_report.get_report.return_value = [('Город',), ('Москва',)]
    mock_report_class.return_value = mock_report

    data = {'reporttype': 'city', 'filetype': 'invalid'}

    response = client.post(reverse('download'), data=data)
    assert response.status_code == 404

    assert mock_logger.info.called


@pytest.mark.integration
@pytest.mark.django_db
@patch('account.views.download.CityReport')
@patch('account.views.download.logger')
def test_download_view_with_group_city_false(
    mock_logger, mock_report_class, client, create_test_user
):
    """Тест скачивания с group_city=False"""
    client.force_login(create_test_user)

    mock_report = Mock()
    mock_report.get_report.return_value = [('Город',), ('Москва',)]
    mock_report_class.return_value = mock_report

    data = {'reporttype': 'city', 'filetype': 'txt'}
    # Не передаём group_city, чтобы использовалось значение по умолчанию

    response = client.post(reverse('download'), data=data)

    assert response.status_code == 200
    # Проверяем, что CityReport был вызван с group_city=False (по умолчанию)
    mock_report_class.assert_called_once_with(create_test_user.id, False)


@pytest.mark.integration
@pytest.mark.django_db
@patch('account.views.download.CityReport')
@patch('account.views.download.logger')
def test_download_view_with_group_city_true(
    mock_logger, mock_report_class, client, create_test_user
):
    """Тест скачивания с group_city=True"""
    client.force_login(create_test_user)

    mock_report = Mock()
    mock_report.get_report.return_value = [('Город',), ('Москва',)]
    mock_report_class.return_value = mock_report

    data = {'reporttype': 'city', 'filetype': 'txt', 'group_city': 'on'}

    response = client.post(reverse('download'), data=data)

    assert response.status_code == 200
    # Проверяем, что CityReport был вызван с group_city='on'
    mock_report_class.assert_called_once_with(create_test_user.id, 'on')


@pytest.mark.integration
@pytest.mark.django_db
@patch('account.views.download.CityReport')
@patch('account.views.download.logger')
def test_download_view_filename_format(mock_logger, mock_report_class, client, create_test_user):
    """Тест формата имени файла при скачивании"""
    client.force_login(create_test_user)

    mock_report = Mock()
    mock_report.get_report.return_value = [('Город',), ('Москва',)]
    mock_report_class.return_value = mock_report

    data = {'reporttype': 'city', 'filetype': 'txt'}

    response = client.post(reverse('download'), data=data)

    assert response.status_code == 200

    content_disposition = response['Content-Disposition']
    assert 'MoiGoroda__' in content_disposition
    assert 'testuser' in content_disposition
    assert '.txt' in content_disposition


@pytest.mark.integration
@pytest.mark.django_db
@patch('account.views.download.CityReport')
@patch('account.views.download.logger')
def test_download_view_multiple_downloads(mock_logger, mock_report_class, client, create_test_user):
    """Тест нескольких последовательных скачиваний"""
    client.force_login(create_test_user)

    mock_report = Mock()
    mock_report.get_report.return_value = [('Город',), ('Москва',)]
    mock_report_class.return_value = mock_report

    # Первое скачивание
    data1 = {'reporttype': 'city', 'filetype': 'txt'}
    response1 = client.post(reverse('download'), data=data1)
    assert response1.status_code == 200

    # Второе скачивание
    data2 = {'reporttype': 'city', 'filetype': 'csv'}
    response2 = client.post(reverse('download'), data=data2)
    assert response2.status_code == 200

    # Проверяем, что оба скачивания прошли успешно
    assert response1['Content-Type'] == 'text/txt'
    assert response2['Content-Type'] == 'text/csv'


@pytest.mark.integration
@pytest.mark.django_db
@patch('account.views.download.CityReport')
@patch('account.views.download.logger')
def test_download_view_empty_report(mock_logger, mock_report_class, client, create_test_user):
    """Тест скачивания пустого отчёта"""
    client.force_login(create_test_user)

    mock_report = Mock()
    mock_report.get_report.return_value = [
        ('Город', 'Регион', 'Дата посещения', 'Наличие сувенира', 'Оценка')
    ]
    mock_report_class.return_value = mock_report

    data = {'reporttype': 'city', 'filetype': 'txt'}

    response = client.post(reverse('download'), data=data)

    assert response.status_code == 200
    content = response.content.decode()
    # Проверяем, что есть заголовки
    assert 'Город' in content
    assert 'Регион' in content


@pytest.mark.integration
@pytest.mark.django_db
@patch('account.views.download.CityReport')
@patch('account.views.download.logger')
def test_download_view_logs_success(mock_logger, mock_report_class, client, create_test_user):
    """Тест что успешное скачивание логируется"""
    client.force_login(create_test_user)

    mock_report = Mock()
    mock_report.get_report.return_value = [('Город',), ('Москва',)]
    mock_report_class.return_value = mock_report

    data = {'reporttype': 'city', 'filetype': 'txt'}

    client.post(reverse('download'), data=data)

    # Проверяем, что логирование произошло
    assert mock_logger.info.call_count >= 1
    last_call = mock_logger.info.call_args_list[-1]
    assert 'Successfully downloaded file' in last_call[0][1]


@pytest.mark.integration
@pytest.mark.django_db
@patch('account.views.download.CityReport')
@patch('account.views.download.logger')
def test_download_view_missing_parameters(mock_logger, mock_report_class, client, create_test_user):
    """Тест скачивания с отсутствующими параметрами"""
    client.force_login(create_test_user)

    mock_report = Mock()
    mock_report.get_report.return_value = [('Город',), ('Москва',)]
    mock_report_class.return_value = mock_report

    # Отсутствует filetype
    data = {'reporttype': 'city'}

    response = client.post(reverse('download'), data=data)
    assert response.status_code == 404
