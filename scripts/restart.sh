#!/usr/bin/expect
# Скрипт перезапускает Gunicorn
set timeout -1
spawn sudo systemctl daemon-reload
expect "password"
send "$env(SUDO_PASSWORD)\r"
spawn sudo systemctl restart gunicorn
expect "password"
send "$env(SUDO_PASSWORD)\r"
expect eof
