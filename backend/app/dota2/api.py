import bz2
import concurrent
import json
import requests
import time
from dota2.scrappers.OpenDotaScrapper import OpenDotaScrapper


validation_values = {
    "duration": 28 * 60,
    "human_players": 10,
    "game_mode": 22
}


class api:

    def __init__(self, key: str):
        self.base_url = 'https://api.steampowered.com/'
        self.OP_scrapper = OpenDotaScrapper()
        self.session = requests.session()

        self.set_headers()
        self.key = key

    def set_headers(self, headers=None):
        with open('./dota2/data/headers.json') as f:
            self.session.headers = json.load(f)

    def get(self, url, params):
        params['key'] = self.key

        res = self.session.get(url, params=params)
        res.raise_for_status()

        return res.json()

    def get_match_history(self, hero_id=None, skill=None, min_players=None, matches_requested=None, start_at_match_id=None):
        end_point = 'IDOTA2Match_570/GetMatchHistory/v1'
        params = {
            "hero_id": hero_id,
            "skill": skill,
            "min_players": min_players,
            "matches_requested": matches_requested,
            "start_at_match_id": start_at_match_id
        }

        matches = self.get(self.base_url + end_point, params)
        return matches['result']['matches']

    def get_match_history_by_sequence_num(self, sequence_num="", matches_requested=100):
        end_point = 'IDOTA2Match_570/GetMatchHistoryBySequenceNum/v1'
        params = {
            "start_at_match_seq_num": sequence_num,
            "matches_requested": matches_requested
        }

        matches = self.get(self.base_url + end_point, params)
        return matches['result']['matches']

    def get_match_details(self, match_id):
        end_point = 'IDOTA2Match_570/GetMatchDetails/v1'
        params = {
            "match_id": match_id
        }

        match = self.get(self.base_url + end_point, params)
        return match['result']

    def get_heroes_data(self):
        end_point = 'IEconDOTA2_570/GetHeroes/v1'

        res = self.get(self.base_url + end_point, params={})
        return res['result']['heroes']

    def get_seq_num(self):
        return self.get_match_history(matches_requested=1)[0]['match_seq_num']

    def get_valid_ranked_games(self, seq_num):
        def is_valid(match):
            return match['duration'] >= validation_values['duration'] and \
                   match['human_players'] == validation_values['human_players'] and\
                   match['game_mode'] == validation_values['game_mode']

        matches = self.get_match_history_by_sequence_num(sequence_num=seq_num)
        valid_matches = list(filter(is_valid, matches))

        next_seq_num = matches[-1]['match_seq_num']
        return valid_matches[0:-1], next_seq_num

    def download_game_replay(self, match_id):
        download_url = self.OP_scrapper.get_replay_url(match_id)

        res = self.session.get(download_url, stream=True)
        res.raise_for_status()

        filepath = f'./replays/{match_id}.dem.bz2'
        with open(filepath, 'wb') as f:
            print(f'Downloading replay#{match_id}')
            for chunk in res.iter_content(1024):
                f.write(chunk)

        with bz2.open(filepath, 'rb') as f:
            content = f.read()

        with open(f'./replays/{match_id}.dem', 'wb') as f:
            f.write(content)

        print(f'Just finished downloading replay#{match_id}')

    def download_games_replays_async(self, matches_id_list):
        start = time.time()

        if len(matches_id_list) > 60:
            print("Can't handle more than 60 API calls per minute")
        else:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(self.download_game_replay, matches_id_list)

        print(f'Spent {round(time.time() - start, 2)} on downloading replays')