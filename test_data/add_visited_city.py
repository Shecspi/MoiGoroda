"""

В этом файле описываются тестовые данные и данные ответа для эндпоинта добавления посещённого города.
Формат данных:
(
    request_data: dict,
    status_code: int,
    correct_response_data: dict,
    log_level: str,
    log_message: str
)

Copyright Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

"""

add_visited_city_test_data = (
    # С данными всё ок
    (
        {
            'city': 1,
            'date_of_visit': '2024-08-01',
            'has_magnet': True,
            'impression': 'impression',
            'rating': 3,
        },
        200,
        {
            'status': 'success',
            'city': {
                'id': 1,
                'city': 1,
                'city_title': 'Город 1',
                'region_title': 'Регион 1 область',
                'date_of_visit': '2024-08-01',
                'has_magnet': True,
                'impression': 'impression',
                'rating': 3,
            },
        },
        'INFO',
        '(API: Add visited city) The visited city has been successfully added from unknown location   /api/city/visited/add',
    ),
    # Не заполнены оба обязательных поля
    (
        {},
        400,
        {'city': ['Обязательное поле.'], 'rating': ['Обязательное поле.']},
        'WARNING',
        '(API: Add visited city) Validation in the serializer failed from unknown location   /api/city/visited/add',
    ),
    # Не заполнено обязательное поле city
    (
        {'city': 1},
        400,
        {'rating': ['Обязательное поле.']},
        'WARNING',
        '(API: Add visited city) Validation in the serializer failed from unknown location   /api/city/visited/add',
    ),
    # Не заполнено обязательное поле rating
    (
        {'rating': 1},
        400,
        {'city': ['Обязательное поле.']},
        'WARNING',
        '(API: Add visited city) Validation in the serializer failed from unknown location   /api/city/visited/add',
    ),
    # Поля city и rating должны успешно обрабатываться, если в них переданы числа в виде строк
    (
        {'city': '1', 'rating': '1'},
        200,
        {
            'status': 'success',
            'city': {
                'id': 2,  # Не понимаю, почему БД не сбрасывается при новом тесте. Поэтому здесь ID = 2.
                'city': 1,
                'city_title': 'Город 1',
                'region_title': 'Регион 1 область',
                'date_of_visit': None,
                'has_magnet': False,
                'impression': None,
                'rating': 1,
            },
        },
        'INFO',
        '(API: Add visited city) The visited city has been successfully added from unknown location   /api/city/visited/add',
    ),
    # Неверный формат поля city
    (
        {'city': 'f', 'rating': '1'},
        400,
        {'city': ['Некорректный тип. Ожидалось значение первичного ключа, получен str.']},
        'WARNING',
        '(API: Add visited city) Validation in the serializer failed from unknown location   /api/city/visited/add',
    ),
    # Неверный формат поля city
    (
        {'city': False, 'rating': '1'},
        400,
        {'city': ['Некорректный тип. Ожидалось значение первичного ключа, получен bool.']},
        'WARNING',
        '(API: Add visited city) Validation in the serializer failed from unknown location   /api/city/visited/add',
    ),
    # Неверный формат поля city
    (
        {'city': ('1',), 'rating': '1'},
        400,
        {'city': ['Некорректный тип. Ожидалось значение первичного ключа, получен list.']},
        'WARNING',
        '(API: Add visited city) Validation in the serializer failed from unknown location   /api/city/visited/add',
    ),
    # Неверный формат поля date_of_visit
    (
        {'city': 1, 'rating': 3, 'date_of_visit': '2022/01/01'},
        400,
        {
            'date_of_visit': [
                'Неправильный формат date. Используйте один из этих форматов: YYYY-MM-DD.'
            ]
        },
        'WARNING',
        '(API: Add visited city) Validation in the serializer failed from unknown location   /api/city/visited/add',
    ),
    # Неверный формат поля date_of_visit
    (
        {'city': 1, 'rating': 3, 'date_of_visit': '01/01/2022'},
        400,
        {
            'date_of_visit': [
                'Неправильный формат date. Используйте один из этих форматов: YYYY-MM-DD.'
            ]
        },
        'WARNING',
        '(API: Add visited city) Validation in the serializer failed from unknown location   /api/city/visited/add',
    ),
    # Неверный формат поля date_of_visit
    (
        {'city': 1, 'rating': 3, 'date_of_visit': '2022-13-01'},
        400,
        {
            'date_of_visit': [
                'Неправильный формат date. Используйте один из этих форматов: YYYY-MM-DD.'
            ]
        },
        'WARNING',
        '(API: Add visited city) Validation in the serializer failed from unknown location   /api/city/visited/add',
    ),
    # Неверный формат поля date_of_visit
    (
        {'city': 1, 'rating': 3, 'date_of_visit': '2022-01-32'},
        400,
        {
            'date_of_visit': [
                'Неправильный формат date. Используйте один из этих форматов: YYYY-MM-DD.'
            ]
        },
        'WARNING',
        '(API: Add visited city) Validation in the serializer failed from unknown location   /api/city/visited/add',
    ),
    # Неверный формат поля date_of_visit
    (
        {'city': 1, 'rating': 3, 'date_of_visit': '01.01.2022'},
        400,
        {
            'date_of_visit': [
                'Неправильный формат date. Используйте один из этих форматов: YYYY-MM-DD.'
            ]
        },
        'WARNING',
        '(API: Add visited city) Validation in the serializer failed from unknown location   /api/city/visited/add',
    ),
    # Неверный формат поля date_of_visit
    (
        {'city': 1, 'rating': 3, 'date_of_visit': '2022.01.01'},
        400,
        {
            'date_of_visit': [
                'Неправильный формат date. Используйте один из этих форматов: YYYY-MM-DD.'
            ]
        },
        'WARNING',
        '(API: Add visited city) Validation in the serializer failed from unknown location   /api/city/visited/add',
    ),
    # Неверный формат поля date_of_visit
    (
        {'city': 1, 'rating': 3, 'date_of_visit': '01-01-2022'},
        400,
        {
            'date_of_visit': [
                'Неправильный формат date. Используйте один из этих форматов: YYYY-MM-DD.'
            ]
        },
        'WARNING',
        '(API: Add visited city) Validation in the serializer failed from unknown location   /api/city/visited/add',
    ),
    # Корректный формат поля date_of_visit
    ({'city': 1, 'rating': 3, 'date_of_visit': '2022-01-01'}, 200, False, False, False),
    # Рейтинг не может быть меньше 1
    (
        {'city': 1, 'rating': 0},
        400,
        {'rating': ['Убедитесь, что это значение больше либо равно 1.']},
        'WARNING',
        '(API: Add visited city) Validation in the serializer failed from unknown location   /api/city/visited/add',
    ),
    # Рейтинг не может быть меньше 1
    (
        {'city': 1, 'rating': -1},
        400,
        {'rating': ['Убедитесь, что это значение больше либо равно 1.']},
        'WARNING',
        '(API: Add visited city) Validation in the serializer failed from unknown location   /api/city/visited/add',
    ),
    # Рейтинг не может быть меньше 1
    (
        {'city': 1, 'rating': -10},
        400,
        {'rating': ['Убедитесь, что это значение больше либо равно 1.']},
        'WARNING',
        '(API: Add visited city) Validation in the serializer failed from unknown location   /api/city/visited/add',
    ),
    # Рейтинг не может быть больше 5
    (
        {'city': 1, 'rating': 6},
        400,
        {'rating': ['Убедитесь, что это значение меньше либо равно 5.']},
        'WARNING',
        '(API: Add visited city) Validation in the serializer failed from unknown location   /api/city/visited/add',
    ),
    # Рейтинг не может быть больше 5
    (
        {'city': 1, 'rating': 10},
        400,
        {'rating': ['Убедитесь, что это значение меньше либо равно 5.']},
        'WARNING',
        '(API: Add visited city) Validation in the serializer failed from unknown location   /api/city/visited/add',
    ),
    # Рейтинг должен быть числом
    (
        {'city': 1, 'rating': 'string'},
        400,
        {'rating': ['Введите правильное число.']},
        'WARNING',
        '(API: Add visited city) Validation in the serializer failed from unknown location   /api/city/visited/add',
    ),
    # Рейтинг не может быть дробным числом
    (
        {'city': 1, 'rating': 3.5},
        400,
        {'rating': ['Введите правильное число.']},
        'WARNING',
        '(API: Add visited city) Validation in the serializer failed from unknown location   /api/city/visited/add',
    ),
    # Рейтинг должен быть в диапазоне от 1 до 5
    ({'city': 1, 'rating': 1}, 200, False, False, False),
    # Рейтинг должен быть в диапазоне от 1 до 5
    ({'city': 1, 'rating': 2}, 200, False, False, False),
    # Рейтинг должен быть в диапазоне от 1 до 5
    ({'city': 1, 'rating': 3}, 200, False, False, False),
    # Рейтинг должен быть в диапазоне от 1 до 5
    ({'city': 1, 'rating': 4}, 200, False, False, False),
    # Рейтинг должен быть в диапазоне от 1 до 5
    ({'city': 1, 'rating': 5}, 200, False, False, False),
    # Рейтинг может быть представлен в виде строки, которая очевидно конвертируется в число
    ({'city': 1, 'rating': '1'}, 200, False, False, False),
    # Рейтинг не может быть представлен в виде строки, которая очевидно не конвертируется в число
    (
        {'city': 1, 'rating': '1a'},
        400,
        {'rating': ['Введите правильное число.']},
        'WARNING',
        '(API: Add visited city) Validation in the serializer failed from unknown location   /api/city/visited/add',
    ),
    # Поле has_magnet должно быть валидным типом bool
    (
        {'city': 1, 'rating': 1, 'has_magnet': True},
        200,
        False,
        False,
        False,
    ),
    # Поле has_magnet должно быть валидным типом bool
    (
        {'city': 1, 'rating': 1, 'has_magnet': False},
        200,
        False,
        False,
        False,
    ),
    # Поле has_magnet должно быть валидным типом bool
    (
        {'city': 1, 'rating': 1, 'has_magnet': 'string'},
        400,
        {'has_magnet': ['Must be a valid boolean.']},
        'WARNING',
        '(API: Add visited city) Validation in the serializer failed from unknown location   /api/city/visited/add',
    ),
    # Поле impression должно быть валидным типом string
    ({'city': 1, 'rating': 1, 'impression': 'string'}, 200, False, False, False),
    # Поле impression должно быть валидным типом string
    ({'city': 1, 'rating': 1, 'impression': 111}, 200, False, False, False),
    # Поле impression должно быть валидным типом string
    (
        {'city': 1, 'rating': 1, 'impression': False},
        400,
        {'impression': ['Not a valid string.']},
        'WARNING',
        '(API: Add visited city) Validation in the serializer failed from unknown location   /api/city/visited/add',
    ),
    # Поле impression должно быть валидным типом string
    (
        {'city': 1, 'rating': 1, 'impression': ['string']},
        400,
        {'impression': ['Not a valid string.']},
        'WARNING',
        '(API: Add visited city) Validation in the serializer failed from unknown location   /api/city/visited/add',
    ),
)
