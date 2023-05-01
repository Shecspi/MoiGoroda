#!/usr/bin/expect
set timeout -1
spawn python3 manage.py collectstatic
expect "Are you sure you want to do this?"
send "yes\r"
expect eof
