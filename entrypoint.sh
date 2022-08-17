#!/bin/bash

cd $HOME

id
# usermod -aG 1001 $USER
# id
# Override user ID lookup to cope with being randomly assigned IDs using
# the -u option to 'docker run'.

USER_ID=$(id -u)

if [ x"$USER_ID" != x"0" -a x"$USER_ID" != x"1001" ]; then
    NSS_WRAPPER_PASSWD=/tmp/passwd.nss_wrapper
    NSS_WRAPPER_GROUP=/etc/group

    cat /etc/passwd | sed -e 's/^hbscorez:/builder:/' > $NSS_WRAPPER_PASSWD

    echo "hbscorez:x:$USER_ID:0:HbScorez,,,:/code:/bin/bash" >> $NSS_WRAPPER_PASSWD

    export NSS_WRAPPER_PASSWD
    export NSS_WRAPPER_GROUP

    LD_PRELOAD=/usr/local/lib64/libnss_wrapper.so
    export LD_PRELOAD
fi
id

touch /code/hbscorez.log
# mkdir -p logs
# touch ./logs/gunicorn.log
# touch ./logs/gunicorn-access.log
# tail -n 0 -f ./logs/gunicorn*.log &

SETTINGS_FILE="/settings.py"
if [ -f "$SETTINGS_FILE" ]
then
    echo "using runtime settings from $SETTINGS_FILE."
    ln -s $SETTINGS_FILE ./src/hbscorez/settings_runtime.py
    export DJANGO_SETTINGS_MODULE=hbscorez.settings_runtime
fi

export PYTHONUNBUFFERED=1
pipenv run ./src/manage.py migrate & ps fauxwww & ls -la
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
        --workers $GUNICORN_WORKERS \
        --log-level=info \
        --log-file=../logs/gunicorn.log \
        --access-logfile=../logs/gunicorn-access.log \
        "$@"
fi
