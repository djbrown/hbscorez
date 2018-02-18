#!/bin/bash
#0 0 * * 5,6 /home/pydev/PycharmProjects/hbscorez/crontask.sh
docker exec -it hbscorez_web_1 python manage.py setup
docker exec -it hbscorez_web_1 python manage.py download_reports
docker exec -it hbscorez_web_1 python manage.py import_scores
