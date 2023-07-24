#!/usr/bin/expect
# Скрипт обновляет конфигурацию systemd и перезапускает Gunicorn
set timeout -1
spawn sudo systemctl daemon-reload && sudo systemctl restart gunicorn
expect "password"
send "$env(SUDO_PASSWORD)\r"
expect eof
