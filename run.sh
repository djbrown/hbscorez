#!/bin/bash
python manage.py migrate
python manage.py create_data --2
python manage.py runserver 0.0.0.0:8000
