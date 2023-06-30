import requests
import json
from bs4 import BeautifulSoup as bs


class BuffScrapper:

    def __init__(self):
        self.base_url = 'https://dotabuff.com/'

        self.session = requests.session()
        with open('./dota2/data/headers.json') as f:
            self.session.headers = json.load(f)

    def get_hero_counters(self, hero: str):
        url = self.base_url + f'heroes/{hero}/counters'

        res = self.session.get(url)
        res.raise_for_status()
        soup = bs(res.content, 'html.parser')

        # find table with heroes
        table = soup.find('table', {"class": 'sortable'})
        heroes_raw_data = table.find_all('tr')

        # get heroes data
        hero_data = {}
        for hero in heroes_raw_data[1:]:
            attrs = [attr.text for attr in hero]
            name = attrs[1].lower().replace(' ', '-').replace("'", '')

            hero_data[name] = {'counter': round(-float(attrs[2][:-1]), 2), 'win_rate': float(attrs[3][:-1])}

        hero_data['avrg_win_rate'] = float(soup.find('div', {'class': "header-content-secondary"}).find('span').text[:-1])
        return hero_data