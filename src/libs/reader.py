'''
reader.py
讀取文檔相關的操作
'''

import re

import numpy as np
from pathlib import Path

from libs.interface.running_window import RunningWindow
from libs.pdxscript import read as pdxread
from libs.root import Root

def read_loc_files(root:Root,running_window:RunningWindow) -> None:
    '''
    讀取本地化文件

    :param prev: 引用的框架
    :param root: 根視窗
    :param result_queue: 結果回傳佇列
    :param progress_queue: 進度回傳佇列
    '''
    #檢驗路徑是否存在
    if root.hoi4path is None:
        running_window.exception = "The path is not given in instance self.root!"
        return

    #估計檔案數(用於進度回傳)
    loc_file_path = Path(root.hoi4path).joinpath(f"localisation/{root.user_lang}")

    #檢驗路徑是否存在
    if not loc_file_path.exists() or not loc_file_path.is_dir():
        running_window.exception= "Invalid path for Heart of Iron IV or mod"
        return

    loc_file_count = sum(1 for file in loc_file_path.rglob("*yml") if file.is_file())

    running_window.localization_data = dict() #儲存輸出結果的字典

    try:
        loc_files = list(loc_file_path.rglob("*yml"))
    
    except PermissionError as e:
        running_window.exception = e
        return

    #檢查是否正確取得本地化文本
    if not loc_files:
        running_window.exception = f"Cannot find any localisation files at {loc_file_path}. Please check your directary."
        return 

    #依序處理每個yml檔並更新進度
    for index,loc_file in enumerate(loc_files):
        read_loc_file(running_window,loc_file)
        if running_window.is_cancel_task:
            break
        running_window.progress_var = int(((index+1)/loc_file_count)*100)
    
    if running_window.is_cancel_task:
        return
    
    #輸出檔案
    return running_window.localization_data

def read_loc_file(prev,loc_file:str) -> None:
    '''
    讀取`loc_file`的本地化文檔

    :param prev: 引用的框架
    :param loc_file: 本地化文檔的路徑
    '''
    pattern = r'(\w+):\s*"([^"]+)"'#形如 keyword : "value"的特徵。
    try:
        with open(file=loc_file,mode="r",encoding="utf-8-sig") as file:
            for line in file:
                match = re.search(pattern, line.strip())
                if match:
                    key, value = match.groups()
                    prev.localization_data[key] = value

                if prev.is_cancel_task:
                    break
    except FileNotFoundError as e:
        prev.exception = e

def read_supply_node_file(file_path:str) -> tuple[int]:
    '''
    讀取補給基地所在的省份

    :param file_path: 檔案位置
    :return: 一串紀錄省分ID的列表
    '''
    with open(file_path,"r",encoding="utf-8") as file:
        result = list()
        for line in file:
            province = line.strip().split(" ")[1]
            result.append(province)
    
    return tuple(result)

def read_railway_file(file_path:str) -> tuple[dict[str,int|list]]:
    '''
    讀取鐵軌所在的省分及等級

    :param file_path: 檔案位置
    :return: 一串象徵每條鐵軌的列表
    '''
    with open(file_path,"r",encoding="utf-8") as file:
        result = list()
        for line in file:
            single_railway_data = line.strip().split(" ")
            railway_level = single_railway_data[0]
            railway_provinces = tuple(single_railway_data[2:len(single_railway_data)])
            result.append({"level":railway_level,
                           "province":railway_provinces})
    return tuple(result)

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
        state_province_mapping = dict()
        state_files = list(state_file_path.rglob("*txt"))

        file_reading = None
        for counter, file in enumerate(state_files):

            file_reading = file
            data = pdxread(file)

            state_id = int(data[0]["id"])

            #列出其擁有的所有省分
            provinces = data[0]["provinces"]
            state_province_mapping[state_id] = provinces
            
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
            strategicregion_id = int(data[0]["id"])
            strategicregion_data[strategicregion_id] = data

            running_window.progress_var = 70+int((counter+1)/strategicregions_file_count)*30

    except Exception as e:
        running_window.exception = f"讀取{file_reading}出現錯誤:{e}"
        return
    
    return {"province":province_definitions,
            "adjacency":adjacencies_data,
            "adjacency_rule":adjacency_rules_data,
            "continent":continent_data,
            "season":seasons_data,
            "supply_node":supply_nodes_data,
            "railway":railway_data,
            "state": state_data,
            "state-province": state_province_mapping,
            "strategicregion":strategicregion_data}