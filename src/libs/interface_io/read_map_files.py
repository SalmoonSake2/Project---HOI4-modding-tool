'''
read_map_files.py

讀取資料夾並獲取地圖資訊
'''

import numpy as np
from pathlib import Path

from libs.interface.running_window import RunningWindow
from libs.root import Root
from libs.pdxscript.pdxscript_convert import read as pdxread
from libs.util.map_data_reader import read_railway_file, read_supply_node_file

def read_map_files(root:Root,running_window:RunningWindow) -> None:
    '''
    讀取地圖檔案，相關技術細節可以參閱\n
    https://hoi4.paradoxwikis.com/Map_modding#Provinces

    :param root: 根視窗
    '''

    map_file_path = Path(root.hoi4path).joinpath("map")
    state_file_path = Path(root.hoi4path).joinpath("history/states")
    strategicregions_file_path = map_file_path.joinpath("strategicregions")

    strategicregions_file_count = sum(1 for file in strategicregions_file_path.rglob("*txt") if file.is_file())
    
    province_definitions_csv_column_names = ("id","r","g","b","type","coastal","category","continent")

    try:
        province_definitions = np.genfromtxt(map_file_path.joinpath("definition.csv"),
                                            delimiter=";",
                                            dtype=None,
                                            encoding="utf-8",
                                            names=province_definitions_csv_column_names)
    except Exception as e:
        running_window.exception = f"讀取definition.csv時出現錯誤:{e}"
        return
    
    try:
        adjacencies_data = np.genfromtxt(map_file_path.joinpath("adjacencies.csv"),
                                        delimiter=";",
                                        dtype=None,
                                        encoding="utf-8",
                                        invalid_raise=False,
                                        names=True)
    except Exception as e:
        running_window.exception = f"讀取adjacencies.csv出現錯誤:{e}"
        return
    
    try:
        adjacency_rules_data = pdxread(map_file_path.joinpath("adjacency_rules.txt"))
    except Exception as e:
        running_window.exception = f"讀取adjacency_rules.txt出現錯誤:{e}"
        return
    
    try:
        continent_data = pdxread(map_file_path.joinpath("continent.txt"))
    except Exception as e:
        running_window.exception = f"讀取continent.txt出現錯誤:{e}"
        return
    
    try:
        seasons_data = pdxread(map_file_path.joinpath("seasons.txt"))
    except Exception as e:
        running_window.exception = f"讀取seasons.txt出現錯誤:{e}"
        return
    
    try:
        supply_nodes_data = read_supply_node_file(map_file_path.joinpath("supply_nodes.txt"))
    except Exception as e:
        running_window.exception = f"讀取supply_nodes.txt出現錯誤:{e}"
        return
    
    try:
        railway_data = read_railway_file(map_file_path.joinpath("railways.txt"))
    except Exception as e:
        running_window.exception = f"讀取railways.txt出現錯誤:{e}"
        return
    
    running_window.progress_var = 30

    try:
        state_data = dict()
        state_files = list(state_file_path.rglob("*txt"))

        file_reading = None
        for counter, file in enumerate(state_files):

            file_reading = file
            data = pdxread(file)
            state_id = int(data[0].value[0].value)
            state_data[state_id] = data

            running_window.progress_var = 30+int((counter+1)/strategicregions_file_count)*40
    
    except Exception as e:
        running_window.exception = f"讀取{file_reading}出現錯誤:{e}"
        return

    try:
        strategicregion_data = dict()
        strategicregion_files = list(strategicregions_file_path.rglob("*txt"))

        for counter, file in enumerate(strategicregion_files):

            file_reading = file
            data = pdxread(file)
            strategicregion_id = int(data[0].value[0].value)
            strategicregion_data[strategicregion_id] = data

            running_window.progress_var = 70+int((counter+1)/strategicregions_file_count)*30

    except Exception as e:
        running_window.exception = f"讀取{file_reading}出現錯誤:{e}"
        return
    
    return {"provionce":province_definitions,
            "adjacency":adjacencies_data,
            "adjacency_rule":adjacency_rules_data,
            "continent":continent_data,
            "season":seasons_data,
            "supply_node":supply_nodes_data,
            "railway":railway_data,
            "state": state_data,
            "strategicregion":strategicregion_data}