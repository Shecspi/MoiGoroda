# <img src="static/image/favicon.ico" height="28"> Moi Goroda
Это проект для контроля и визуализации посещённых городов России, написанный на языке Python 3.10 и фреймворке Django 4.1.  
Работающий пример Вы можете посмотреть на сайте [moi-goroda.ru](https://moi-goroda.ru/).  
Исходный код распространяется под лицензией [Apache License 2.0](https://github.com/Shecspi/MoiGoroda/blob/master/LICENSE).  

![Python 3.10](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)
![Django 4.2](https://img.shields.io/badge/Django-4.2-brightgreen?style=for-the-badge&logo=django)
[![Apache License 2.0](https://img.shields.io/badge/License-Apache%20License%202.0-orange?style=for-the-badge&logo=apache)](https://github.com/Shecspi/MoiGoroda/blob/master/LICENSE)

## :floppy_disk: Установка
0. Подготовить директорию, в которой будет располагаться проект, и перейти в неё.
1. Скачать репозиторий  
```shell
git clone https://github.com/Shecspi/MoiGoroda.git .
```
2. Установить необходимую версию Python  
 ```shell
 pyenv install $(cat .python-version)
 ```
3. Удалить текущее виртуальное окружение (если оно есть), создать новое и устанавить все зависимости  
```shell
if [ -n $(poetry env info -p) ]; then rm -rf $(poetry env info -p); fi;
poetry env use $(cat .python-version);
poetry install;
```
4. В папке `MoiGoroga` скопировать файл `.env.example` в `.env` и указать в нём актуальные настройки
5. Сделать миграции  
```shell
poetry run python3 manage.py makemigrations && poetry run python3 manage.py migrate
```
6. Создать суперпользователя
```shell
poetry run python3 manage.py createsuperuser
```
7. Создать папку для хранения статичных файлов (если её ещё не существует), изменить ей владельца и сделать сборку статичных файлов
```shell
if [ ! -d '/var/www' ]; then sudo mkdir /var/www; fi;
sudo chown www:www /var/www;
poetry run python3 manage.py collectstatic
```
9. Загрузить изначальные настройки базы данных (федеральные округа, регионы, города)  
```shell
poetry run python3 manage.py loaddata db.json
```
11. Перезапустить сервер

## :bomb: Тестирование
Для тестирование используются модули `pytest` и `pytest-django`. Эти зависимости прописаны в `pyproject.toml`.  
Чтобы запустить тесты выполните команду в корневой директории проекта
```shell
poetry run pytest
```
