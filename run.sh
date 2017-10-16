#!/bin/bash
python manage.py migrate
python manage.py download_reports
python manage.py create_data
python manage.py runserver 0.0.0.0:8000
