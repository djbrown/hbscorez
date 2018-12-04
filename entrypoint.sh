#!/bin/bash

mkdir -p logs
touch ./logs/gunicorn.log
touch ./logs/gunicorn-access.log
tail -n 0 -f ./logs/gunicorn*.log &

SETTINGS_FILE="/settings.py"
if [ -f "$SETTINGS_FILE" ]
then
    echo "using runtime settings from $SETTINGS_FILE."
    ln -s $SETTINGS_FILE ./hbscorez/settings_runtime.py
    export DJANGO_SETTINGS_MODULE=hbscorez.settings_runtime
fi

export PYTHONUNBUFFERED=1
pipenv run python manage.py migrate || { echo "could not apply migrations. stopping startup.. "; exit 5; }

if [[ -z "${GUNICORN_WORKERS}" ]]; then
    echo "no gunicorn workers specified -> running with dev server"
    exec pipenv run python manage.py runserver 0.0.0.0:8000 "$@"
else
    pipenv run python manage.py collectstatic --noinput
    exec pipenv run gunicorn hbscorez.wsgi:application \
        --name hbscorez_django \
        --bind 0.0.0.0:8000 \
        --workers $GUNICORN_WORKERS \
        --log-level=info \
        --log-file=./logs/gunicorn.log \
        --access-logfile=./logs/gunicorn-access.log \
        "$@"
fi
