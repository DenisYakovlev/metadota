import requests
from scrappers import default_headers, BuffScrapper, OpenDotaScrapper
import time
import concurrent.futures
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os, shutil, bz2
import tensorflow as tf
import joblib
import random
from datetime import datetime
import pandas as pd
# from sklearn.preprocessing import StandardScaler


validation_values = {
    "duration": 28 * 60,
    "human_players": 10,
    "game_mode": 22
}

hero_extensions = {
    1: "anti-mage",
    11: "shadow-fiend",
    20: "vengeful-spirit",
    21: "windranger",
    22: "zeus",
    36: "necrophos",
    39: "queen-of-pain",
    42: "wraith-king",
    51: "clockwerk",
    53: "natures-prophet",
    54: "lifestealer",
    69: "doom",
    76: "outworld-destroyer",
    83: "treant-protector",
    91: "io",
    96: "centaur-warrunner",
    97: "magnus",
    98: "timbersaw",
    108: "underlord"
}

ann = tf.keras.models.load_model('prediction model 2')
scaler = joblib.load('Scaler2.save')
ColumnTransformer = joblib.load('ColumnTransformer.save')


def clean_replays_folder():
    dirpath = './replays'

    for filename in os.listdir(dirpath):
        filepath = os.path.join(dirpath, filename)
        try:
            shutil.rmtree(filepath)
        except OSError:
            os.remove(filepath)

    print('Cleaned replays folder')


def get_match_stage(match_time):
    game_stages = {
        'early game': 60 * 17,
        'mid game': 60 * 27,
        'late game': 60 * 37
    }

    time_delta = datetime.strptime(match_time, "%H:%M:%S") - datetime(1900,1,1)
    game_time = time_delta.total_seconds()

    for stage, timestamp in game_stages.items():
        if game_time < timestamp:
            return stage

    return 'superlate game'


def update_heroes_data(key):
    handler = GamesHandler(key)
    with open('heroes_data.json', 'w') as f:
        json.dump(handler.load_heroes_data(), f)


class api:

    def __init__(self, key: str):
        self.base_url = 'https://api.steampowered.com/'
        self.OP_scrapper = OpenDotaScrapper()
        self.session = requests.session()

        self.set_headers()
        self.key = key

    def set_headers(self, headers=None):
        self.session.headers = headers or default_headers

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


class ReplaysHandler:

    @staticmethod
    def extract_heroes_names(game_data):
        data = {}
        heroes_data = GamesHandler.get_heroes_data()
        heroes_id = [player['hero_id'] for player in game_data]

        for id in heroes_id:
            hero = next(hero for hero in heroes_data['heroes'] if hero['id'] == id)
            data[f'hero_{len(data)}'] = GamesHandler.extract_hero_name(hero)

        return data

    @staticmethod
    def extract_replay_data(heroes_data, match_details):
        radiant, dire = heroes_data[0:5], heroes_data[5:]
        game_heroes = ReplaysHandler.extract_heroes_names(heroes_data)

        get_net_worth = lambda team: sum([player['gold'] for player in team])
        get_exp = lambda team: sum([player['xp'] for player in team])
        get_kills = lambda team: sum([player['kills'] for player in team])
        counter_data = GamesHandler.calculate_counters(list(game_heroes.values()))

        data = {
            'match_id': match_details['match_id'],
            **game_heroes,
            'match_time': time.strftime('%H:%M:%S', time.gmtime(match_details['match_time'])),
            'game_stage': get_match_stage(match_details['match_time']),
            'counter': counter_data['counter'],
            'net_worth_diff': round(get_net_worth(radiant) - get_net_worth(dire)),
            'exp_diff': round(get_exp(radiant) - get_exp(dire)),
            'score_diff': get_kills(radiant) - get_kills(dire),
            'radiant_win': int(match_details['radiant_win'])
        }

        return data

    @staticmethod
    def parse_replay(filepath):
        parser_address = 'http://localhost:5600'

        with open(filepath, 'rb') as f:
            replay_data = f.read()

        try:
            res = requests.post(url=parser_address, data=replay_data)
            game_data = '[' + res.content.decode('utf-8').replace('\n', ',')[:-1] + ']'
            game_data = json.loads(game_data)

            heroes_data = [frame for frame in game_data if frame['type'] == 'interval' and frame['time'] >= 0]
            raw_match_details = json.loads(next(frame for frame in game_data if frame['type'] == 'epilogue')['key'])
            game_duration = int(len(heroes_data) / 10)

            match_details = {
                'match_id': raw_match_details['gameInfo_']['dota_']['matchId_'],
                'radiant_win': raw_match_details['gameInfo_']['dota_']['gameWinner_'] == 2
            }

            game_stages = {
                'early_game_stage': random.randrange(0, 60 * 17),
                'mid_game_stage': 60 * 17 + random.randrange(0, 60 * 10),
            }
            if game_duration > 60 * 37:
                game_stages['late_game_stage'] = 60 * 27 + random.randrange(0, 60 * 10)
                game_stages['superlate_game_stage'] = 60 * 37 + random.randrange(0, game_duration - 60 * 37)
            else:
                game_stages['late_game_stage'] = 60 * 27 + random.randrange(0, game_duration - 60 * 27)

            output = []
            for stage in game_stages.values():
                output.append(ReplaysHandler.extract_replay_data(heroes_data[stage * 10:(stage + 1) * 10],
                                                                 {**match_details, 'match_time': stage}))

            return output

        except Exception:
            print("Parser is not working.")
            quit()


class GamesHandler:

    def __init__(self, api_key: str):
        self.api = api(api_key)
        self.scrapper = BuffScrapper()

    @staticmethod
    def extract_hero_name(hero):
        if hero['id'] in hero_extensions.keys():
            return hero_extensions[hero['id']]

        return hero['name'][14:].replace('_', '-')

    @staticmethod
    def get_heroes_data():
        with open('heroes_data.json', 'r') as f:
            return json.load(f)

    @staticmethod
    def calculate_counters(heroes):
        data = GamesHandler.get_heroes_data()
        radiant, dire = heroes[0:5], heroes[5:]
        result = [0, 0, 0, 0, 0]

        for i, d_hero in enumerate(dire):
            for r_hero in radiant:
                result[i] -= data['counters'][d_hero][r_hero]['counter']

        return {"counter": round(sum(result),2)}

    @staticmethod
    def extract_heroes_from_game(game):
        data = {}
        heroes_data = GamesHandler.get_heroes_data()
        heroes_id = [player['hero_id'] for player in game['players']]

        for id in heroes_id:
            hero = next(hero for hero in heroes_data['heroes'] if hero['id'] == id)
            data[f'hero_{len(data)}'] = GamesHandler.extract_hero_name(hero)

        return data

    @staticmethod
    def extract_data_from_recorded_game(game):
        radiant, dire = game['players'][0:5], game['players'][5:]
        game_duration = game['duration']
        game_heroes = GamesHandler.extract_heroes_from_game(game)

        get_net_worth = lambda team: sum([player['gold_per_min'] * game_duration / 60 for player in team])
        get_exp = lambda team: sum([player['xp_per_min'] * game_duration / 60 for player in team])
        counter_data = GamesHandler.calculate_counters(list(game_heroes.values()))

        data = {
            'match_id': game['match_id'],
            **game_heroes,
            'duration': time.strftime('%H:%M:%S', time.gmtime(game_duration)),
            'counter': counter_data['counter'],
            'net_worth_diff': round(get_net_worth(radiant) - get_net_worth(dire)),
            'exp_diff': round(get_exp(radiant) - get_exp(dire)),
            'score_diff': game['radiant_score'] - game['dire_score'],
            'radiant_win': int(game['radiant_win'])
        }

        return data

    @staticmethod
    def extract_data_from_ongoing_game(game):
        data = {}

        if 'team2' in game['player']:
            game_duration = game['map']['clock_time']
            radiant, dire = {"players": game['player']['team2'], 'heroes': game['hero']['team2']}, \
                            {"players": game['player']['team3'], 'heroes': game['hero']['team3']}

            get_net_worth = lambda team: sum([player['net_worth'] + player['gold'] for player in team.values()])
            get_exp = lambda team: sum([player['xpm'] * game_duration / 60 for player in team.values()])
            get_kills = lambda team: sum([player['kills'] for player in team.values()])
            get_heroes = lambda team: [GamesHandler.extract_hero_name(hero) for hero in team.values()]

            r_heroes, d_heroes = get_heroes(radiant['heroes']), get_heroes(dire['heroes'])

            data = {
                "match id": game['map']['matchid'],
                "game time": time.strftime('%H:%M:%S', time.gmtime(game_duration)),
                "net worth diff": round(get_net_worth(radiant['players']) - get_net_worth(dire['players'])),
                "exp diff": round(get_exp(radiant['players']) - get_exp(dire['players'])),
                "score diff": get_kills(radiant['players']) - get_kills(dire['players']),
                "radiant heroes": ' '.join(r_heroes),
                "dire heroes": ' '.join(d_heroes),
                "counter": GamesHandler.calculate_counters([*r_heroes, *d_heroes])['counter'],
            }

            prediction_values = ColumnTransformer.transform([[get_match_stage(data['game time']), data["counter"],
                                                   data["net worth diff"], data["exp diff"], data["score diff"]]])

            data['Radiant win change'] = round(float(ann.predict(scaler.transform(prediction_values))[0][0]), 2)
        else:
            data = {'msg': 'You are in menu or playing private match. No data can be parsed'}

        return data

    def load_heroes_data(self):
        heroes_data = self.api.get_heroes_data()
        heroes_names = [self.extract_hero_name(hero) for hero in heroes_data]

        heroes_counters = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for hero, counters in zip(heroes_names, executor.map(self.scrapper.get_hero_counters, heroes_names)):
                heroes_counters[hero] = counters

        print('Loaded Heroes data')
        return {'heroes': heroes_data, 'counters': heroes_counters}

    def record_last_games(self, games_limit=10000, await_time=10):
        recorded_games = []
        seq_num = self.api.get_seq_num()

        games_counter = 0
        while games_counter < games_limit:
            matches, seq_num = self.api.get_valid_ranked_games(seq_num)
            games_counter += len(matches)

            recorded_games.append(matches)
            time.sleep(await_time)
            print(f'\rRecorded {games_counter} games', flush=True, end='')

        print('')
        return sum(recorded_games, [])

    def process_dataset(self, dataset=[]):
        print('Processing dataset')

        dataset = list(dataset)
        processed_data = list(map(self.extract_data_from_recorded_game, dataset))
        return processed_data


class requestHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def log_message(self, format, *args):
        pass

    def do_POST(self):
        self._set_headers()

        self.send_response(200)
        self.end_headers()

        content_len = int(self.headers.get('Content-Length'))
        game_data = json.loads(self.rfile.read(content_len))
        data = GamesHandler.extract_data_from_ongoing_game(game_data)

        os.system("cls")
        for key, value in data.items():
            print(f'{key}: {value}')

        return


class GSI:

    def __init__(self, address='localhost', port=3000):
        self.PORT = port
        self.sever_address = (address, self.PORT)
        self.server = HTTPServer(self.sever_address, requestHandler)

    def __del__(self):
        self.server.shutdown()

    def start(self):
        print(f'Server running on port {self.PORT}')
        self.server.serve_forever()


