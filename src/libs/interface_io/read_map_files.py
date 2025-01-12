'''
read_map_files.py

讀取資料夾並獲取地圖資訊
'''

import queue

import pandas as pd
from pathlib import Path

from libs.root import Root
from libs.pdxscript.pdxscript_convert import read as pdxread
from libs.util.map_data_reader import read_railway_file, read_supply_node_file

def read_map_files(prev,root:Root,result_queue:queue.Queue, progress_queue:queue.Queue) -> None:
    '''
    讀取地圖檔案，相關技術細節可以參閱\n
    https://hoi4.paradoxwikis.com/Map_modding#Provinces

    :param root: 根視窗
    :param result_queue: 結果回傳佇列
    :param progress_queue: 進度回傳佇列
    '''

    map_file_path = Path(root.hoi4path).joinpath("map")
    strategicregions_file_path = map_file_path.joinpath("strategicregions")

    strategicregions_file_count = sum(1 for file in strategicregions_file_path.rglob("*txt") if file.is_file())
    
    province_definitions_csv_column_names = ("id","r","g","b","type","coastal","category","continent")
    column_names = province_definitions_csv_column_names

    province_definitions = pd.read_csv(map_file_path.joinpath("definition.csv"),
                                        header=None,
                                        names=column_names)
    adjacencies_data = pd.read_csv(map_file_path.joinpath("adjacencies.csv"))
    adjacency_rules_data = pdxread(map_file_path.joinpath("adjacency_rules.txt").as_posix())
    continent_data = pdxread(map_file_path.joinpath("continent.txt").as_posix())
    seasons_data = pdxread(map_file_path.joinpath("seasons.txt").as_posix())
    supply_nodes_data = read_supply_node_file(map_file_path.joinpath("supply_nodes.txt").as_posix())
    railway_data = read_railway_file(map_file_path.joinpath("railways.txt").as_posix())
    
    progress_queue.put(50)

    strategicregion_data = dict()
    strategicregion_files = list(strategicregions_file_path.rglob("*txt"))
    for counter, file in enumerate(strategicregion_files):
        data = pdxread(file)
        strategicregion_id = int(data[0].value[0].value)
        strategicregion_data[strategicregion_id] = data
        progress_queue.put(50+int((counter+1)/strategicregions_file_count)*50)
    
    result_queue.put({"provionce":province_definitions,
                        "adjacency":adjacencies_data,
                        "adjacency_rule":adjacency_rules_data,
                        "continent":continent_data,
                        "season":seasons_data,
                        "supply_node":supply_nodes_data,
                        "railway":railway_data,
                        "strategicregion":strategicregion_data})