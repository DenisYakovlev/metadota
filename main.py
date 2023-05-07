import time, os
import dota2
from dota2 import clean_replays_folder
import pandas as pd
import concurrent.futures


# def parse_async():
#     replays = [os.path.abspath('./replays/' + filename) for filename in os.listdir('./replays') if
#                filename.endswith('.dem')]
#     start_parse = time.time()
#     with concurrent.futures.ThreadPoolExecutor(5) as executor:
#         data = executor.map(ReplaysHandler.parse_replay, replays)
#
#     print(f'Spent {time.time() - start_parse} on parsing')
#     return data
#
#
# def test_parse_matches():
#     start = time.time()
#
#     dataset = GameHandler.record_last_games(3000, 10)
#     data = GameHandler.process_dataset(dataset)
#
#     df = pd.DataFrame.from_dict(data)
#     df.to_csv(data_file, mode='a', index=False, headers=False)
#
#     print('\n', time.time() - start)
#
#
# def test_parse_replays(index):
#     start = time.time()
#
#     matches = pd.read_csv(data_file)
#     id_list = list(matches.iloc[:, 1])
#
#     for i in range(index, len(id_list) // 50):
#         if len(os.listdir('./replays')) == 0:
#             matches_to_download = id_list[i * 50: (i + 1) * 50]
#             api.download_games_replays_async(matches_to_download)
#
#         data = parse_async()
#         clean_replays_folder()
#         data = sum(data, [])
#
#         df = pd.DataFrame.from_dict(data)
#         df.to_csv(output_file, mode='a', index=False, header=False)
#
#         del data, df
#
#     print('\n', time.time() - start)
#
#
# def get_parse_index():
#     df = pd.read_csv(data_file)
#     match_id = pd.read_csv(output_file).tail(1).match_id.values[0]
#     return df.loc[df.match_id == match_id].values[0][0] // 50 + 1


with open('key.txt') as f:
    key = f.read()


GameHandler = dota2.GamesHandler(key)
ReplaysHandler = dota2.ReplaysHandler()
api = dota2.api(key)
ReplaysHandler.parse_replay('./6164183390_868602124.dem')
# server = dota2.GSI()
# server.start()