import json
import os
import random
import shutil
import time
import datetime
import requests

from MetaDota.gsi.dota2.handlers.GameHandler import GamesHandler


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