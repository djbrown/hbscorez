#!/bin/bash
python manage.py migrate
python manage.py create_data --exemplary
python manage.py runserver 0.0.0.0:8000
