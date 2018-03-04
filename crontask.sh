#!/bin/bash
#0 0 * * 5,6
set -e
source ~/.bash_profile
workon hbscorez
export DJANGO_SETTINGS_MODULE=hbscorez.settings_prod
#python manage.py setup
python manage.py import_games
python manage.py download_reports
python manage.py import_scores
