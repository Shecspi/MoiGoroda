"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from unittest.mock import Mock, patch

import pytest

from services.logger import info, warning


@pytest.mark.unit
@patch('services.logger.logging.getLogger')
def test_info_logs_message(mock_get_logger: Mock) -> None:
    """Тест что функция info логирует сообщение"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_request = Mock()
    mock_request.get_full_path.return_value = '/test/path'
    mock_request.user.username = 'testuser'

    info(mock_request, 'Test message')

    mock_logger.info.assert_called_once()
    call_args = mock_logger.info.call_args
    assert 'Test message' in call_args[0][0]
    assert '/test/path' in call_args[0][0]


@pytest.mark.unit
@patch('services.logger.logging.getLogger')
def test_info_with_custom_logger(mock_get_logger: Mock) -> None:
    """Тест что функция info использует кастомный логгер"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_request = Mock()
    mock_request.get_full_path.return_value = '/test/path'
    mock_request.user.username = 'testuser'

    info(mock_request, 'Test message', logger_name='custom_logger')

    mock_get_logger.assert_called_once_with('custom_logger')


@pytest.mark.unit
@patch('services.logger.logging.getLogger')
def test_info_with_guest_user(mock_get_logger: Mock) -> None:
    """Тест что функция info обрабатывает гостевого пользователя"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_request = Mock()
    mock_request.get_full_path.return_value = '/test/path'
    mock_request.user.username = ''

    info(mock_request, 'Test message')

    mock_logger.info.assert_called_once()
    call_args = mock_logger.info.call_args
    assert call_args[1]['extra']['user'] == '<GUEST>'


@pytest.mark.unit
@patch('services.logger.logging.getLogger')
def test_info_includes_ip(mock_get_logger: Mock) -> None:
    """Тест что функция info включает IP адрес"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_request = Mock()
    mock_request.get_full_path.return_value = '/test/path'
    mock_request.user.username = 'testuser'
    mock_request.META = {'REMOTE_ADDR': '192.168.1.1'}

    info(mock_request, 'Test message')

    mock_logger.info.assert_called_once()
    call_args = mock_logger.info.call_args
    assert call_args[1]['extra']['IP'] == '192.168.1.1'


@pytest.mark.unit
@patch('services.logger.logging.getLogger')
def test_warning_logs_message(mock_get_logger: Mock) -> None:
    """Тест что функция warning логирует сообщение"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_request = Mock()
    mock_request.get_full_path.return_value = '/test/path'
    mock_request.user.username = 'testuser'

    warning(mock_request, 'Warning message')

    mock_logger.warning.assert_called_once()
    call_args = mock_logger.warning.call_args
    assert 'Warning message' in call_args[0][0]
    assert '/test/path' in call_args[0][0]


@pytest.mark.unit
@patch('services.logger.logging.getLogger')
def test_warning_with_custom_logger(mock_get_logger: Mock) -> None:
    """Тест что функция warning использует кастомный логгер"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_request = Mock()
    mock_request.get_full_path.return_value = '/test/path'
    mock_request.user.username = 'testuser'

    warning(mock_request, 'Warning message', logger_name='custom_logger')

    mock_get_logger.assert_called_once_with('custom_logger')


@pytest.mark.unit
@patch('services.logger.logging.getLogger')
def test_warning_with_guest_user(mock_get_logger: Mock) -> None:
    """Тест что функция warning обрабатывает гостевого пользователя"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_request = Mock()
    mock_request.get_full_path.return_value = '/test/path'
    mock_request.user.username = ''

    warning(mock_request, 'Warning message')

    mock_logger.warning.assert_called_once()
    call_args = mock_logger.warning.call_args
    assert call_args[1]['extra']['user'] == '<GUEST>'


@pytest.mark.unit
@patch('services.logger.logging.getLogger')
def test_warning_includes_ip(mock_get_logger: Mock) -> None:
    """Тест что функция warning включает IP адрес"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_request = Mock()
    mock_request.get_full_path.return_value = '/test/path'
    mock_request.user.username = 'testuser'
    mock_request.META = {'REMOTE_ADDR': '192.168.1.1'}

    warning(mock_request, 'Warning message')

    mock_logger.warning.assert_called_once()
    call_args = mock_logger.warning.call_args
    assert call_args[1]['extra']['IP'] == '192.168.1.1'


@pytest.mark.unit
@patch('services.logger.logging.getLogger')
def test_info_with_x_forwarded_for(mock_get_logger: Mock) -> None:
    """Тест что функция info использует X-Forwarded-For заголовок"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_request = Mock()
    mock_request.get_full_path.return_value = '/test/path'
    mock_request.user.username = 'testuser'
    mock_request.META = {
        'HTTP_X_FORWARDED_FOR': '10.0.0.1, 192.168.1.1',
        'REMOTE_ADDR': '192.168.1.1',
    }

    info(mock_request, 'Test message')

    mock_logger.info.assert_called_once()
    call_args = mock_logger.info.call_args
    assert call_args[1]['extra']['IP'] == '10.0.0.1'


@pytest.mark.unit
@patch('services.logger.logging.getLogger')
def test_info_handles_exception_in_ip_extraction(mock_get_logger: Mock) -> None:
    """Тест что функция info обрабатывает исключение при извлечении IP"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_request = Mock()
    mock_request.get_full_path.return_value = '/test/path'
    mock_request.user.username = 'testuser'
    # Устанавливаем META так, чтобы вызвать исключение
    mock_request.META = None

    info(mock_request, 'Test message')

    mock_logger.info.assert_called_once()
    call_args = mock_logger.info.call_args
    assert call_args[1]['extra']['IP'] == 'X.X.X.X'
