import requests
import json


class OpenDotaScrapper:

    def __init__(self,):
        self.base_url = 'https://api.opendota.com/api'

        self.session = requests.session()
        with open('./dota2/data/headers.json') as f:
            self.session.headers = json.load(f)

    def get_replay_url(self, match_id):
        url = self.base_url + '/replays'

        params = {'match_id': match_id}
        res = requests.get(url, params=params)
        res.raise_for_status()

        values = res.json()[0]

        return f"http://replay{values['cluster']}.valve.net/570/{values['match_id']}_{values['replay_salt']}.dem.bz2"