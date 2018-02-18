#!/bin/bash
#0 0 * * 5,6 /home/pydev/PycharmProjects/hbscorez/crontask.sh
sudo docker exec -it hbscorez_web_1 python manage.py setup
sudo docker exec -it hbscorez_web_1 python manage.py import_games
sudo docker exec -it hbscorez_web_1 python manage.py download_reports
sudo docker exec -it hbscorez_web_1 python manage.py import_games
