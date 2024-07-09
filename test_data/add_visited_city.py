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
)
