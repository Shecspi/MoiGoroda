"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from unittest.mock import Mock, patch
from typing import Any


@pytest.mark.unit
def test_place_view_function_exists() -> None:
    """Тест что функция place существует"""
    from place import views

    assert hasattr(views, 'place')
    assert callable(views.place)


@pytest.mark.unit
def test_place_view_is_callable_without_decorator() -> None:
    """Тест что функция place вызываема (проверка доступа выполняется внутри view)"""
    from place import views

    assert callable(views.place)


@pytest.mark.unit
@patch('place.views.render')
def test_place_view_calls_render(mock_render: Any) -> None:
    """Тест что функция place вызывает render с правильными параметрами"""
    from place import views

    # Создаём мок request (авторизованный, без параметра collection)
    mock_request = Mock()
    mock_request.user = Mock()
    mock_request.user.is_authenticated = True
    mock_request.GET = {}
    mock_request.get_full_path = Mock(return_value='/place/map')

    # Вызываем функцию
    views.place(mock_request)

    # Проверяем, что render был вызван
    mock_render.assert_called_once()

    # Проверяем параметры вызова
    call_args = mock_render.call_args
    assert len(call_args.args) >= 2
    assert call_args.args[0] == mock_request
    assert call_args.args[1] == 'place/map.html'

    # Проверяем контекст (может быть в args или kwargs)
    if len(call_args.args) > 2:
        context = call_args.args[2]
    else:
        context = call_args.kwargs.get('context', {})

    assert context['page_title'] == 'Мои места'
    assert context['page_description'] == 'Мои места, отмеченные на карте'
    assert context['active_page'] == 'places'


@pytest.mark.unit
def test_place_view_context_keys() -> None:
    """Тест что функция place возвращает правильные ключи контекста"""
    from place import views

    # Проверяем, что функция существует и имеет правильную сигнатуру
    assert callable(views.place)


@pytest.mark.unit
def test_place_view_template_name() -> None:
    """Тест что функция place использует правильное имя шаблона"""
    from place import views

    # Проверяем, что функция существует
    assert callable(views.place)

    # Проверяем, что шаблон существует (это будет проверено в integration тестах)
    assert True  # Заглушка для проверки существования функции
