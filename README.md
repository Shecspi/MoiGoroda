# <img src="static/image/favicon.ico" height="28"> Moi Goroda
Это проект для контроля и визуализации посещённых городов России, написанный на языке Python и фреймворке Django.  
Работающий пример Вы можете посмотреть на сайте [moi-goroda.ru](https://moi-goroda.ru/).  
Исходный код распространяется под лицензией [Apache License 2.0](https://github.com/Shecspi/MoiGoroda/blob/master/LICENSE).  

![Python 3.12](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![Poetry 1.8](https://img.shields.io/badge/Poetry-1.8-4cae58?style=for-the-badge&logo=poetry)
![Pyenv](https://img.shields.io/badge/Pyenv-gray?style=for-the-badge&logo=.env)
![Pytest 7.4](https://img.shields.io/badge/Pytest-7.4-lightblue?style=for-the-badge&logo=pytest)
![Django 4.2](https://img.shields.io/badge/Django-4.2-darkgreen?style=for-the-badge&logo=django)
![Bootstrap 5.3](https://img.shields.io/badge/Bootstrap-5.3-ac83f7?style=for-the-badge&logo=bootstrap)
[![Apache License 2.0](https://img.shields.io/badge/License-Apache%20License%202.0-orange?style=for-the-badge&logo=apache)](https://github.com/Shecspi/MoiGoroda/blob/master/LICENSE)

## :floppy_disk: Установка
1. Скачать репозиторий  
```shell
git clone https://github.com/Shecspi/MoiGoroda.git && cd MoiGoroda
```
2. Установить необходимую версию Python  
 ```shell
 if [[ "$(pyenv versions 2> /dev/null)" != *"$(cat .python-version )"* ]]; then pyenv install $(cat .python-version); fi
 ```
3. Удалить текущее виртуальное окружение (если оно есть), создать новое и устанавить все зависимости. В случае установки для разработки необходимо из последней команды убрать опцию `--only main`.
```shell
if [ -n $(poetry env info -p) ]; then rm -rf $(poetry env info -p); fi;
poetry env use $(cat .python-version);
poetry install --only main;
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
7. Создать папку для хранения статичных файлов (если её ещё не существует), изменить ей владельца и сделать сборку статичных файлов.
Это необходимо в случае размещения проекта на сервере с настройкой `DEBUG=False`. В случае локального размещения этот пункт можно пропустить.
```shell
if [ ! -d '/var/www' ]; then sudo mkdir /var/www; fi;
sudo chown www:www /var/www;
poetry run python3 manage.py collectstatic
```
8. Загрузить изначальные настройки базы данных (федеральные округа, регионы, города)  
```shell
poetry run python3 manage.py loaddata db.json
```
9. Перезапустить сервер

## :bomb: Тестирование
Для тестирование используются модули `pytest` и `pytest-django`. Эти зависимости прописаны в `pyproject.toml`.  
Чтобы запустить тесты выполните команду в корневой директории проекта
```shell
poetry run pytest
```
