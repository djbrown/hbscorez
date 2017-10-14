import requests
from django.core.management import BaseCommand
from lxml import html

from scorers.models import District, League, Player, Score, Team


class Command(BaseCommand):
    def handle(self, *args, **options):
        Score.objects.all().delete()
        Player.objects.all().delete()
        Team.objects.all().delete()
        League.objects.all().delete()
        District.objects.all().delete()

        districts = [
            ('BWOL', 'Baden-Württemberg Oberliga', 35, 4),
            ('BHV', 'Badischer Handball-Verband', 35, 35),
            ('BzN', 'Bezirk Nord', 35, 84),
            ('BzS', 'Bezirk Süd', 35, 43),
            ('BR', 'Bruchsal', 35, 36),
            ('HD', 'Heidelberg', 35, 37),
            ('KA', 'Karlsruhe', 35, 38),
            ('MA', 'Mannheim', 35, 39),
            ('PF', 'Pforzheim', 35, 40),
        ]
        for d_num, d_data in enumerate(districts):
            district = District(name=d_data[1], abbreviation=d_data[0])
            district.save()
            self.log('District {}/{}: {}'.format(d_num + 1, len(districts), district))

            url = 'http://spo.handball4all.de/Spielbetrieb/index.php'
            data = {
                'orgGrpID': d_data[2],
                'orgID': d_data[3],
            }
            district_response = requests.post(url=url, data=data)

            district_tree = html.fromstring(district_response.text)
            league_links = district_tree.xpath('//*[@id="results"]/div/table[2]/tr/td[1]/a')

            for l_num, league_link in enumerate(league_links):
                league_url = 'http://spo.handball4all.de/Spielbetrieb/index.php' + league_link.get('href')
                league_response = requests.get(league_url)

                league_tree = html.fromstring(league_response.text)
                heading = league_tree.xpath('//*[@id="results"]/div/h1/text()[2]')[0]
                league_name = heading.split(' - ')[0].encode("latin-1").decode()
                league_abbreviation = league_link.text

                league = League(name=league_name, abbreviation=league_abbreviation, district=district)
                league.save()
                self.log('League {}/{}: {}'.format(l_num + 1, len(league_links), league))

                teams = league_tree.xpath('//*[@id="results"]/div/div[2]/table')#/tr[2]/td[3]/a')
                print(teams)
                exit()


    def log(self, text: str) -> None:
        self.stdout.write(self.style.SUCCESS(text))
