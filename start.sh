#!/usr/bin/env bash
chmod -R 777 /usr/local/lib/python3.7
chmod -R 777 /app/static/temp_data
echo "permissions set"

service nginx start
echo "nginx started"
uwsgi --ini uwsgi.ini
echo "uwsgi started"
