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

### Список регионов с законченым списком городов
1. Адыгея
2. Алтай
3. Алтайский край
4. Амурская область
5. Архангельская область
6. Астраханская область
7. Белгородская область
8. Брянская область
9. Калужская область
10. Москва
11. Московская область
12. Тверская область