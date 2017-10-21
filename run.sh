#!/bin/bash
python manage.py migrate
python manage.py create_data --mode 3
python manage.py runserver 0.0.0.0:8000
