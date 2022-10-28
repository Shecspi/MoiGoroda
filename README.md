# How to install

1. Скачать репозиторий `git clone https://github.com/Shecspi/MoiGoroda.git`
2. В папке `MoiGoroga/` переименовать файл `.env.example` в `.env` и указать в нём актуальные настройки
3. Перезапустить сервер `touch ~/moi-goroda.rf/tmp/restart.txt`


## PostgreSQL
1. Установить PostgreSQL `sudo apt install postgresql`
2. Установить пакеты Python `pip install psycopg2-binary`
3. Залогиниться в интерактивную сессию PostgreSQL `sudo -u postgres psql`
4. Создать новую базу данных для Django проекта `CREATE DATABASE db_name;`
5. Создать пользователя базы данных `CREATE USER db_user WITH PASSWORD 'db_password';`
6. Изменить некоторые параметры
   * `ALTER ROLE db_user SET client_encoding TO 'utf8';`
   * `ALTER ROLE db_user SET default_transaction_isolation TO 'read committed';`;
   * `ALTER ROLE db_user SET timezone TO 'UTC';`
7. Дать пользователю права доступа к базе данных `GRANT ALL PRIVILEGES ON DATABASE db_name TO db_user;`
8. Выйти `\q`

## Глобальные настройки
1. 

## Django
1. `./manage.py migrate`;
2. Создать суперпользователя `./manage.py createsuperuser`;
3. Импортировать изначальную базу данных `./manage.py loaddata db.json`
