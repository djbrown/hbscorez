#!/bin/bash

mkdir -p logs
touch ./logs/gunicorn.log
touch ./logs/gunicorn-access.log
tail -n 0 -f ./logs/gunicorn*.log &

SETTINGS_FILE="/settings.py"
if [ -f "$SETTINGS_FILE" ]
then
    echo "using runtime settings from $SETTINGS_FILE."
    ln -s $SETTINGS_FILE ./src/hbscorez/settings_runtime.py
    export DJANGO_SETTINGS_MODULE=hbscorez.settings_runtime
fi

export PYTHONUNBUFFERED=1
pipenv run ./src/manage.py migrate || { echo "could not apply migrations. stopping startup.. "; exit 5; }
pipenv run ./src/manage.py correct_data || { echo "could not correct_data. stopping startup.. "; exit 6; }

if [[ -z "${GUNICORN_WORKERS}" ]]; then
    echo "no gunicorn workers specified -> running with dev server"
    exec pipenv run ./src/manage.py runserver 0.0.0.0:8000 "$@"
else
    pipenv run ./src/manage.py collectstatic --noinput
    exec pipenv run gunicorn hbscorez.wsgi:application \
        --chdir src \
        --name hbscorez_django \
        --bind 0.0.0.0:8000 \
        --workers "$GUNICORN_WORKERS" \
        --log-level=info \
        --log-file=../logs/gunicorn.log \
        --access-logfile=../logs/gunicorn-access.log \
        "$@"
fi
