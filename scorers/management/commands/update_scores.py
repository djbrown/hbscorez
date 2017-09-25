import re

import os
import requests
import tabula as tabula
from django.conf import settings
from django.core.management import BaseCommand
from lxml import html

from scorers.models import PlayerScore

REPORTS_DIR = settings.BASE_DIR + "/reports/"


def parse_penalty_data(text: str) -> (int, int):
    match = re.match("([0-9]+)/([0-9]+)", text)
    if match:
        return match.group(1), match.group(2)
    return 0, 0


class Command(BaseCommand):
    def handle(self, *args, **options):
        PlayerScore.objects.all().delete()
        self._download_reports()
        self._insert_data()

    def _download_reports(self):
        league_id = 26777
        schedule_base_url = "http://spo.handball4all.de/Spielbetrieb/index.php?orgGrpID=35&all=1&score="
        url = schedule_base_url + str(league_id)
        response = requests.get(url)
        self.stdout.write(self.style.SUCCESS('Successfully downloaded reports website'))

        tree = html.fromstring(response.text)
        game_report_urls = tree.xpath('//div[@id="results"]/div/table[2]/tr/td[11]/a/@href')
        self.stdout.write('%d reports found' % len(game_report_urls))
        for url in game_report_urls:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            content_disposition = response.headers['Content-Disposition']
            file_name = content_disposition[22:-1]
            file_path = REPORTS_DIR + file_name
            with open(file_path, 'wb') as file:
                file.write(response.content)

    def _insert_data(self):
        file_names = os.listdir(REPORTS_DIR)
        max_scores = len(file_names) * 2 * 18
        current_scores = 0
        for file_name in file_names:
            file_path = REPORTS_DIR + file_name
            pdf = tabula.read_pdf(file_path, output_format='json', encoding='cp1252', **{'pages': 2, 'lattice': True})
            for table in pdf:
                table_rows = table['data']
                for table_row in table_rows[2:]:
                    row_data = [cell['text'] for cell in table_row]
                    # player_number = row_data[0]
                    player_name = row_data[1]
                    # player_year_of_birth = row_data[2]
                    goals_total = row_data[5] or 0
                    penalty_tries, penalty_goals = parse_penalty_data(row_data[6])
                    # warning_time = row_data[7]
                    # first_suspension_time = row_data[8]
                    # second_suspension_time = row_data[9]
                    # third_suspension_time = row_data[10]
                    # disqualification_time = row_data[11]
                    # report_time = row_data[12]
                    # team_suspension_time = row_data[13]

                    if not player_name:
                        max_scores -= 1
                        continue

                    PlayerScore(
                        player_name=player_name,
                        goals=goals_total,
                        penalty_goals=penalty_goals
                    ).save()

                    current_scores += 1

                    self.stdout.write('Progress: {:.2f}%'.format(float(current_scores) / max_scores * 100), ending='\r')
