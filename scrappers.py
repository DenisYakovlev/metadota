import requests
from bs4 import BeautifulSoup as bs

default_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "Accept-Encoding": "br, gzip, deflate",
    "Content-Type": "application/json"
}


class BuffScrapper:

    def __init__(self):
        self.base_url = 'https://dotabuff.com/'

        self.session = requests.session()
        self.session.headers = default_headers

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


class OpenDotaScrapper:

    def __init__(self,):
        self.base_url = 'https://api.opendota.com/api'

        self.session = requests.session()
        self.session.headers = default_headers

    def get_replay_url(self, match_id):
        url = self.base_url + '/replays'

        params = {'match_id': match_id}
        res = requests.get(url, params=params)
        res.raise_for_status()

        values = res.json()[0]

        return f"http://replay{values['cluster']}.valve.net/570/{values['match_id']}_{values['replay_salt']}.dem.bz2"