import requests
from django.conf import settings
from django.core.management import BaseCommand
from lxml import html

REPORTS_DIR = settings.BASE_DIR + "/reports/"


class Command(BaseCommand):
    def handle(self, *args, **options):
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
