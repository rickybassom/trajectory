#!/usr/bin/env bash
python -c "import sys;print(sys.path)"
service nginx start
uwsgi --ini uwsgi.ini
