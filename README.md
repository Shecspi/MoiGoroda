# ![Image alt](https://github.com/Shecspi/MoiGoroda/blob/master/static/favicon.ico) Moi Goroda
Это проект для контроля и визуализации посещённых городов России, написанный на языке Python 3.10 и фреймворке Django 4.1.  
Работающий пример Вы можете посмотреть на сайте [moi-goroda.ru](https://moi-goroda.ru/).  
Исходный код распространяется под лицензией [Apache License 2.0](https://github.com/Shecspi/MoiGoroda/blob/master/LICENSE).  

![Python 3.10](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)
![Django 4.1](https://img.shields.io/badge/Django-4.1-brightgreen?style=for-the-badge&logo=django)
[![Apache License 2.0](https://img.shields.io/badge/License-Apache%20License%202.0-orange?style=for-the-badge&logo=apache)](https://github.com/Shecspi/MoiGoroda/blob/master/LICENSE)

# Установка

1. Скачать репозиторий  
  `git clone https://github.com/Shecspi/MoiGoroda.git`
2. Установить все зависимости  
  `pip install -r requirements.txt`
3. В папке `MoiGoroga/` переименовать файл `.env.example` в `.env` и указать в нём актуальные настройки
4. Создать папку `logs` в корне проекта
5. Сделать миграции  
  `~/.local/bin/python3.10 ./manage.py makemigrations`  
  `~/.local/bin/python3.10 ./manage.py migrate`
6. Создать суперпользователя
  `~/.local/bin/python3.10 ./manage.py createsuperuser`
7. Настроить выдачу статичных файлов. Сначала в `MoiGoroda/settings.py` добавить переменную (в данном случае Nginx забирает статику из public_html/)  
`STATIC_ROOT = os.path.join(BASE_DIR, './public_html/static')`
8. Выполнить команду  
`~/.local/bin/python3.10 ./manage.py collectstatic`
9. Загрузить изначальные настройки базы данных (федеральные округа, регионы, города)  
  `~/.local/bin/python3.10 ./manage.py loaddata db.json`
10. Перезапустить сервер `touch ~/moi-goroda.rf/tmp/restart.txt`

# Сделать дамп БД
`python3 ./manage.py dumpdata travel.city travel.region travel.area --indent 2 > db.json`
