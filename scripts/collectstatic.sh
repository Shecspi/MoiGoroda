#!/usr/bin/expect
# Скрипт собирает статику для Nginx
set timeout -1
spawn /home/www/.local/bin/poetry run python3 manage.py collectstatic
expect "Are you sure you want to do this?"
send "yes\r"
expect eof
