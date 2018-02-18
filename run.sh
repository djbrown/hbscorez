#!/bin/bash
python manage.py migrate
python manage.py setup
python manage.py download_reports
python manage.py import_scores
python manage.py runserver 0.0.0.0:8000
