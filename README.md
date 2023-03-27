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