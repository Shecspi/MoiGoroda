# ![Image alt](./static/favicon.ico) Moi Goroda
Это проект для контроля и визуализации посещённых городов России, написанный на языке Python 3.10 и фреймворке Django 4.1.  
Работающий пример Вы можете посмотреть на сайте [moi-goroda.ru](https://moi-goroda.ru/).  
Исходный код распространяется под лицензией [Apache License 2.0](https://github.com/Shecspi/MoiGoroda/blob/master/LICENSE).  

![Python 3.10](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)
![Django 4.1](https://img.shields.io/badge/Django-4.1-brightgreen?style=for-the-badge&logo=django)
[![Apache License 2.0](https://img.shields.io/badge/License-Apache%20License%202.0-orange?style=for-the-badge&logo=apache)](https://github.com/Shecspi/MoiGoroda/blob/master/LICENSE)

## :floppy_disk: Установка
1. Скачать репозиторий  
  ```bash
  git clone https://github.com/Shecspi/MoiGoroda.git
  ```
2. Установить все зависимости  
  ```python
  poetry install
  ```
3. В папке `MoiGoroga` скопировать файл `.env.example` в `.env` и указать в нём актуальные настройки
4. В файле `MoiGoroda/settings.py` указать домен или IP-адрес сайта в директиве `ALLOW_HOSTS`, а также указать нужную директорию для статичных файлов `STATIC_ROOT`. 
5. Сделать миграции  
```python
poetry run python3 manage.py makemigrations && poetry run python3 manage.py migrate
```
6. Создать суперпользователя
```python
poetry run python3 manage.py createsuperuser
```
7. Настроить выдачу статичных файлов. Для этого выполнить команду  
```python
python3 manage.py collectstatic
```
9. Загрузить изначальные настройки базы данных (федеральные округа, регионы, города)  
```python
poetry run python3 manage.py loaddata db.json
```
11. Перезапустить сервер

## :bomb: Тестирование
Для тестирование используются модули `pytest` и `pytest-django`. Эти зависимости прописаны в `pyproject.toml`.  
Чтобы запустить тесты выполните команду в корневой директории проекта
```bash
poetry run pytest
```
