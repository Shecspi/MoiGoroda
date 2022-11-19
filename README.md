# Установка

1. Скачать репозиторий  
  `git clone https://github.com/Shecspi/MoiGoroda.git`
2. Установить все зависимости  
  `pip install -r requirements.txt`
3. В папке `MoiGoroga/` переименовать файл `.env.example` в `.env` и указать в нём актуальные настройки
4. Сделать миграции  
  `~/.local/bin/python3.10 ./manage.py makemigrations`  
  `~/.local/bin/python3.10 ./manage.py migrate`
5. Создать суперпользователя
  `~/.local/bin/python3.10 ./manage.py createsuperuser`
6. Настроить выдачу статичных файлов. Сначала в `MoiGoroda/settings.py` добавить переменную (в данном случае Nginx забирает статику из public_html/)  
`STATIC_ROOT = os.path.join(BASE_DIR, './public_html/static')`
7. Выполнить команду  
`~/.local/bin/python3.10 ./manage.py collectstatic`
8. Загрузить изначальные настройки базы данных (федеральные округа, регионы, города)  
  `~/.local/bin/python3.10 ./manage.py loaddata db.json`
9. Перезапустить сервер `touch ~/moi-goroda.rf/tmp/restart.txt`

# Сделать дамп БД
`python3 ./manage.py dumpdata travel.city travel.region travel.area --indent 2 > db.json`