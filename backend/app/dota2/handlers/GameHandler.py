import concurrent
import json
import time
from datetime import datetime
import tensorflow as tf
import joblib
from dota2.api import api
from dota2.scrappers.BuffScrapper import BuffScrapper
# from sklearn.preprocessing import StandardScaler

ann = tf.keras.models.load_model("./dota2/prediction model")
scaler = joblib.load('./dota2/Scaler.save')
ColumnTransformer = joblib.load('./dota2/ColumnTransformer.save')

steamcload_url = "https://cdn.cloudflare.steamstatic.com/"


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

def extract_player_slots(slots):
    data = []
    
    with open("./dota2/data/items.json") as f:
        items_data = json.load(f)
        
        
    for slot in slots.values():
        if slot["name"] == "empty":
            data.append(slot)
        else:  
            normalized_name = slot["name"][5:]
            
            data.append({
                "name": normalized_name,
                "img": steamcload_url + items_data[normalized_name]["img"]
            })
            
    return data
        
def get_match_predictions(data):
    transform_data = lambda data: scaler.transform(ColumnTransformer.transform([data]))
    ann_predict = lambda data: round(float(ann.predict(data)[0][0]), 2)
    
    winrate_prediction_values = transform_data([get_match_stage(data['game']['game_time']),
                                                        data['game']["counter"], data['game']["net_worth_diff"],
                                                        data['game']["exp_diff"], data['game']["score_diff"]])
    
    game_stages_prediction_values = {                
        "early game": transform_data(['early game', data['game']['counter'], 0, 0, 0]),
        "mid game": transform_data(['mid game', data['game']['counter'], 0, 0, 0]),
        "late game": transform_data(['late game', data['game']['counter'], 0, 0, 0]),
        "superlate game": transform_data(['late game', data['game']['counter'], 0, 0, 0])
    }

    return {
        "radiant_win_chance": ann_predict(winrate_prediction_values),
        "early_game": ann_predict(game_stages_prediction_values["early game"]),
        "mid_game": ann_predict(game_stages_prediction_values["mid game"]),
        "late_game": ann_predict(game_stages_prediction_values["late game"]),
        "superlate_game": ann_predict(game_stages_prediction_values["superlate game"]),
    }
   
    
class GamesHandler:

    def __init__(self, api_key: str):
        self.api = api(api_key)
        self.scrapper = BuffScrapper()

    @staticmethod
    def extract_hero_name(hero):
        with open('./dota2/data/hero_extensions.json', 'r') as f:
            hero_extensions = json.load(f)

        # if str(hero['id']) in hero_extensions.keys():
        #     return hero_extensions[str(hero['id'])]
        
        with open('./dota2/data/hero_names.json', 'r') as f:
            hero_links = json.load(f)
        
        hero_data = hero_links[hero['name']]

        return {
            "name": hero_data["localized_name"],
            "img": steamcload_url + hero_data["img"]
        }
        
    @staticmethod
    def extract_hero_name_counter(hero):
        with open('./dota2/data/hero_extensions.json', 'r') as f:
            hero_extensions = json.load(f)

        if str(hero['id']) in hero_extensions.keys():
            return hero_extensions[str(hero['id'])]

        return hero['name'][14:].replace('_', '-')

    # TODO
    @staticmethod
    def extract_heroes_items(game):
        grouped_items = game['items']
        result = []

        for group in grouped_items:
            for player in group:
                items = map(lambda x: x['name'], player.values())


    @staticmethod
    def get_heroes_data():
        with open('./dota2/data/heroes_data.json', 'r') as f:
            return json.load(f)

    @staticmethod
    def calculate_counters(heroes):
        data = GamesHandler.get_heroes_data()
        radiant, dire = heroes[0:5], heroes[5:]
        result = [0, 0, 0, 0, 0]

        for i, d_hero in enumerate(dire):
            for r_hero in radiant:
                result[i] -= data['counters'][d_hero][r_hero]['counter']

        return {"counter": round(sum(result), 2)}

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
                            
                            
            get_stats = lambda team: [[player['kills'], player['assists'], player['deaths'], player['gpm'], player['xpm']]  for player in team.values()]
            get_team_net_worth = lambda team: sum([player['net_worth'] + player['gold'] for player in team.values()])
            get_team_exp = lambda team: sum([player['xpm'] * game_duration / 60 for player in team.values()])
            get_team_kills = lambda team: sum([player['kills'] for player in team.values()])
            get_heroes = lambda team: [GamesHandler.extract_hero_name(hero) for hero in team.values()]
            get_heroes_counter = lambda team: [GamesHandler.extract_hero_name_counter(hero) for hero in team.values()]

            r_heroes, d_heroes, = get_heroes(radiant['heroes']), get_heroes(dire['heroes'])
            r_stats, d_stats = get_stats(radiant['players']), get_stats(dire['players'])
            r_counters, d_counters = get_heroes_counter(radiant['heroes']), get_heroes_counter(dire['heroes'])

            data['status'] = {
                "is_going": True
            }
            data['game'] = {
                "match_id": game['map']['matchid'],
                "game_time": time.strftime('%H:%M:%S', time.gmtime(game_duration)),
                "net_worth_diff": round(get_team_net_worth(radiant['players']) - get_team_net_worth(dire['players'])),
                "exp_diff": round(get_team_exp(radiant['players']) - get_team_exp(dire['players'])),
                "score_diff": get_team_kills(radiant['players']) - get_team_kills(dire['players']),
                "radiant_heroes": {"heroes": r_heroes,"stats": r_stats},
                "dire_heroes": {"heroes": d_heroes,"stats": d_stats},
                "counter": GamesHandler.calculate_counters([*r_counters, *d_counters])['counter'],
            }
            
            data['game']['predictions'] = get_match_predictions(data)
            data['game']['radiant_items'] = {f"player_{idx}": extract_player_slots(slots) for idx, slots in enumerate(game['items']['team2'].values())}
            data['game']['dire_items'] = {f"player_{idx}": extract_player_slots(slots) for idx, slots in enumerate(game['items']['team3'].values())}
            
        else:
            data['status'] = {
                "is_going": False
            }
            data['game'] = {'msg': 'You are in menu or playing private match. No data can be parsed'}

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