'''
reader.py
讀取文檔相關的操作
'''
import re
import traceback as tb

from pathlib import Path
from PIL import Image

from libs.enums import *
from libs.interface.running_window import RunningWindow
from libs.map import *
from libs.misc.buildings import BuildingData
from libs.pdxscript import read as pdxread
from libs.pdxscript import PDXstatement
from libs.root import root

def check_path_avalibility(running_window:RunningWindow) -> None:
    '''
    確認路徑有效性
    '''

    running_window.update_progress(0)

    #檢驗路徑是否存在
    if root.path.hoi4path is None:
        running_window.exception = "尚未設定 Heart of Iron IV 路徑，請設定路徑後重新讀取"
        return
    
    running_window.update_progress(25)

    #確認遊戲路徑是否正常
    if not Path(root.path.hoi4path).joinpath("hoi4.exe").exists():
        running_window.exception = "無效的 Heart of Iron IV 路徑，請確認路徑後重新讀取"
        return
    
    running_window.update_progress(50)

    #確認模組路徑是否正常
    if root.path.modpath is not None:
        if not Path(root.path.modpath).joinpath("descriptor.mod").exists():
            running_window.exception = f"無效的模組路徑{path}，確認該模組已包含正確的descriptor.mod後再重試"
            return
        
    running_window.update_progress(75)

    #確認引用模組路徑正常
    for path in root.path.included_modpaths:
        if not Path(path).joinpath("descriptor.mod").exists():
            running_window.exception = f"無效的引用模組路徑{path}，確認該模組已包含正確的descriptor.mod後再重試"
            return
        
        #用戶中斷
        if running_window.is_cancel_task: return
    
    running_window.update_progress(100)

def integrate_path(running_window:RunningWindow) -> None:
    '''
    整合本體遊戲、模組的路徑，優先級高的路徑在後
    '''

    running_window.update_progress(0)

    avalible_path = [root.path.hoi4path]
    avalible_path.extend(root.path.included_modpaths)

    running_window.update_progress(90)

    if root.path.modpath is not None:
        avalible_path.extend([root.path.modpath])

    root.path.avalible_path = avalible_path

    running_window.update_progress(100)

def get_mod_name(path:str) -> str:
    '''
    獲取模組名稱

    :param path: 模組資料夾所在路徑
    '''

    try:
        mod_name = PDXstatement("mod",pdxread(path+"/descriptor.mod"))["name"].strip('"')
        mod_version =  PDXstatement("mod",pdxread(path+"/descriptor.mod"))["version"].strip('"')
    except:
        raise Exception(f"模組讀取失敗:{path}")
    
    return f"{mod_name}({mod_version})"
    
def read_loc_files(running_window:RunningWindow) -> None:
    '''
    讀取本地化文件
    '''

    #找出本地化文件的路徑
    loc_files = dict()

    for loc_dir in root.path.avalible_path:

        loc_file_dir = Path(loc_dir).joinpath("localisation")

        en_loc_file_list = list(loc_file_dir.rglob(f"*l_english.yml"))
        native_loc_file_list = list(loc_file_dir.rglob(f"*l_{root.mod_lang}.yml"))

        en_loc_file_list.extend(native_loc_file_list)

        #確保同名檔案只會出現一次
        for file in en_loc_file_list:
            loc_files[file.name] = file
    
    #replace底下的檔案

    replace_loc_files = dict()
    for loc_dir in root.path.avalible_path:

        replace_loc_file_dir = Path(loc_dir).joinpath("localisation/replace")

        replce_en_loc_file_list = list(replace_loc_file_dir.rglob(f"*l_english.yml"))
        replace_native_loc_file_list = list(replace_loc_file_dir.rglob(f"*l_{root.mod_lang}.yml"))

        replce_en_loc_file_list.extend(replace_native_loc_file_list)

        for file in replce_en_loc_file_list:
            replace_loc_files[file.name] = file

    for counter1, loc_file in enumerate(loc_files.values()):

        read_loc_file(running_window,loc_file)

        running_window.update_progress(int((counter1+1)/(len(loc_files)+len(replace_loc_files))*100))
        
        if running_window.is_cancel_task:return
    
    for counter2, loc_file in enumerate(replace_loc_files.values()):

        read_loc_file(running_window,loc_file)

        running_window.update_progress(int((counter2+counter1+1)/(len(loc_files)+len(replace_loc_files))*100))
        
        if running_window.is_cancel_task:return

def read_loc_file(running_window:RunningWindow,loc_file:str) -> None:
    '''
    讀取`loc_file`的本地化文檔

    :param loc_file: 本地化文檔的路徑
    '''

    #形如 keyword :0"value"的特徵。
    loc_pattern = r'(^\w+):\s*\d*?\s*"([^"]+)"'

    #讀取檔案並找尋翻譯字串加入到本地化資料中
    with open(file=loc_file,mode="r",encoding="utf-8-sig") as file:

        for line in file:

            match = re.search(loc_pattern, line.strip())

            if match:
                key, value = match.groups()
                root.game_loc[key] = value

            if running_window.is_cancel_task: break

def read_map_files(running_window:RunningWindow) -> None:
    '''                                                   
    讀取地圖檔案，相關技術細節可以參閱\n
    https://hoi4.paradoxwikis.com/Map_modding#Provinces

    :param root: 根視窗
    '''
    import numpy as np

    running_window.update_progress(0)
    print("正在處理圖像")

    #讀取圖像(heightmap.bmp、provinces.bmp、rivers.bmp、terrain.bmp)
    for path in root.path.avalible_path:
        try: root.game_image.heightmap_image = Image.open(path +"/map/heightmap.bmp")
        except FileNotFoundError: pass
        except Exception as e:
            running_window.exception = f"處理以下檔案時發生錯誤:{path+"/map/heightmap.bmp"},{e}"
            print(fc.RED+tb.format_exc()+fc.CC)
            return

    for path in root.path.avalible_path:
        try: root.game_image.province_image = Image.open(path + "/map/provinces.bmp")
        except FileNotFoundError: pass
        except Exception as e:
            running_window.exception = f"處理以下檔案時發生錯誤:{path + "/map/provinces.bmp"},{e}"
            print(fc.RED+tb.format_exc()+fc.CC)
            return

    for path in root.path.avalible_path:
        try: root.game_image.rivers_image = Image.open(path +"/map/rivers.bmp")
        except FileNotFoundError: pass
        except Exception as e:
            running_window.exception = f"處理以下檔案時發生錯誤:{path +"/map/rivers.bmp"},{e}"
            print(fc.RED+tb.format_exc()+fc.CC)
            return

    for path in root.path.avalible_path:
        try: root.game_image.terrain_image = Image.open(path +"/map/terrain.bmp")
        except FileNotFoundError: pass
        except Exception as e:
            running_window.exception = f"處理以下檔案時發生錯誤:{path +"/map/terrain.bmp"},{e}"
            print(fc.RED+tb.format_exc()+fc.CC)
            return
    
    running_window.update_progress(5)
    print("正在處理map/definition.csv")

    #處理省分定義(definition.csv)
    province_definitions_csv_column_names = ("id","r","g","b","type","coastal","category","continent")

    for path in root.path.avalible_path:
        try:
            province_array = np.genfromtxt(Path(path).joinpath("map").joinpath("definition.csv"),
                                                 delimiter=";",
                                                 dtype=None,
                                                 encoding="utf-8",
                                                 names=province_definitions_csv_column_names)
            
            root.map_data.province = dict()

            for index, data in enumerate(province_array):
                
                #第一項是垃圾
                if index == 0: continue

                color = (data["r"],data["g"],data["b"])

                root.map_data.color_mapping.avalible_color.add(color)

                #將資料調整成 id: Province的字典
                root.map_data.province[data["id"]] = Province(id=data["id"],
                                                              color=color,
                                                              type=data["type"],
                                                              terrain=data["category"],
                                                              coastal= True if data["coastal"] else False,
                                                              continent=data["continent"])
                
                #建立顏色查詢表
                root.map_data.color_mapping.province_id_from_color[color] = data["id"]

                if running_window.is_cancel_task: return

        except FileNotFoundError: pass
        except Exception as e:
            running_window.exception = f"處理以下檔案時發生錯誤:{Path(path).joinpath("map").joinpath("definition.csv")},{e}"
            print(fc.RED+tb.format_exc()+fc.CC)
            return
    
    del path, province_array, index, data, color

    running_window.update_progress(15)
    print("正在處理map/adjacencies.csv")

    #處理省分連結(adjacencies.csv)
    #文件的最後一行必須是-1;-1;-1;-1;-1;-1;-1;-1;-1
    for path in root.path.avalible_path:
        file_reading = Path(path).joinpath("map").joinpath("adjacencies.csv")
        try:
            adjacencies_array = np.genfromtxt(Path(path).joinpath("map").joinpath("adjacencies.csv"),
                                             delimiter=";",
                                             dtype=None,
                                             encoding="utf-8",
                                             invalid_raise=False,
                                             names=True)
            
            for data in adjacencies_array:
                adjacencies = Adjacency(data["From"],
                                          data["To"],
                                          data["Type"],
                                          data["Through"],
                                          (data["start_x"],data["start_y"]),
                                          (data["stop_x"],data["stop_y"]),
                                          data["adjacency_rule_name"])
                
                root.map_data.adjacencies.add(adjacencies)

                if running_window.is_cancel_task: return

        except FileNotFoundError: pass
        except Exception as e:
            running_window.exception = f"處理以下檔案時發生錯誤:{file_reading},{e}"
            print(fc.RED+tb.format_exc()+fc.CC)
            return
    
    del path, file_reading, adjacencies_array, data, adjacencies

    running_window.update_progress(20)
    print("正在處理map/adjacency_rules.txt")

    #處理省分連結規則(adjacency_rules.txt)
    for path in root.path.avalible_path:

        try: 
            file_reading = Path(path).joinpath("map").joinpath("adjacency_rules.txt")
            adjacency_rules_data = pdxread(Path(path).joinpath("map").joinpath("adjacency_rules.txt"))

            #逐一讀取每一條規則

            relationships = ("contested","enemy","friend","neutral")

            for statement in adjacency_rules_data:
                name = statement["name"].strip('"')
                required_provinces = statement["required_provinces"]
                is_disabled = statement["is_disabled"]
                icon = statement["icon"]
                offset = statement["offset"]

                #逐一讀取不同關係下的通過規則
                passing_rule = dict()

                for relationship in relationships:

                    army_rule = True if statement[relationship]["army"] == "yes" else False
                    navy_rule = True if statement[relationship]["navy"] == "yes" else False
                    submarine_rule = True if statement[relationship]["submarine"] == "yes" else False
                    trade_rule = True if statement[relationship]["trade"] == "yes" else False

                    passing_rule[relationship] = (army_rule,navy_rule,submarine_rule,trade_rule)
                
                #紀錄
                root.map_data.adjacency_rules[name] = AdjacencyRule(name=name,
                                                                    contested=passing_rule["contested"],
                                                                    enemy=passing_rule["enemy"],
                                                                    friend=passing_rule["friend"],
                                                                    neutral=passing_rule["neutral"],
                                                                    required_provinces=required_provinces,
                                                                    is_disabled=is_disabled,
                                                                    icon=icon,
                                                                    offset=offset)
                
                if running_window.is_cancel_task: return

        except FileNotFoundError: pass
        except Exception as e:
            running_window.exception = f"處理以下檔案時發生錯誤:{file_reading},{e}"
            print(fc.RED+tb.format_exc()+fc.CC)
            return

    del path, file_reading, adjacency_rules_data, relationships, statement, name, required_provinces, is_disabled, icon, offset
    del passing_rule, relationship, army_rule, navy_rule,submarine_rule, trade_rule

    running_window.update_progress(25)
    print("正在處理map/continent.txt")

    #處理大陸(continent.txt)
    for path in root.path.avalible_path:
        file_reading = Path(path).joinpath("map").joinpath("continent.txt")
        try: 
            continents = pdxread(Path(path).joinpath("map").joinpath("continent.txt"))[0].value

            for index, name in enumerate(continents):

                root.map_data.continents[index+1] = name

                if running_window.is_cancel_task: return

        except FileNotFoundError: pass
        except Exception as e:
            running_window.exception = f"處理以下檔案時發生錯誤:{file_reading},{e}"
            print(fc.RED+tb.format_exc()+fc.CC)
            return
    
    del path, file_reading, continents, index, name

    running_window.update_progress(27)
    print("正在處理map/supply_nodes.txt")

    #處理補給基地(supply_nodes.txt)
    for path in root.path.avalible_path:
        file_reading = Path(path).joinpath("map").joinpath("supply_nodes.txt")
        try: root.map_data.supply_nodes = read_supply_node_file(Path(path).joinpath("map").joinpath("supply_nodes.txt"))
        except FileNotFoundError: pass
        except Exception as e:
            running_window.exception = f"處理以下檔案時發生錯誤:{file_reading},{e}"
            print(fc.RED+tb.format_exc()+fc.CC)
            return

    del path, file_reading

    running_window.update_progress(30)
    print("正在處理map/railways.txt")

    #處理鐵路(railways.txt)
    for path in root.path.avalible_path:
        file_reading = Path(path).joinpath("map").joinpath("railways.txt")
        try: root.map_data.railways = read_railway_file(Path(path).joinpath("map").joinpath("railways.txt"))
        except FileNotFoundError: pass
        except Exception as e:
            running_window.exception = f"處理以下檔案時發生錯誤:{file_reading},{e}"
            print(fc.RED+tb.format_exc()+fc.CC)
            return
    
    del path, file_reading

    running_window.update_progress(35)
    print("正在處理map/unitstacks.txt")

    #處理物件位置(unitstacks.txt)，事實上我只關心victory_point的位置
    unitstack_column_names = ("id","type","x","y","z","rotation","offset")

    for path in root.path.avalible_path:
        try:
            file_reading = Path(path).joinpath("map").joinpath("unitstacks.txt")
            unitstacks_array = np.genfromtxt(Path(path).joinpath("map").joinpath("unitstacks.txt"),
                                            delimiter=";",
                                            dtype=None,
                                            encoding="utf-8",
                                            invalid_raise=False,
                                            names=unitstack_column_names)
            VICTORY_POINT_SYMBOL = 38
            victory_points = unitstacks_array[unitstacks_array["type"] == VICTORY_POINT_SYMBOL]

            for victory_point in victory_points:

                root.map_data.province[victory_point["id"]].pos = (victory_point["x"],victory_point["z"])

                if running_window.is_cancel_task: return

        except FileNotFoundError: pass
        except Exception as e:
            running_window.exception = f"處理以下檔案時發生錯誤:{file_reading},{e}"
            print(fc.RED+tb.format_exc()+fc.CC)
            return
    
    del path, file_reading, unitstacks_array, VICTORY_POINT_SYMBOL, victory_points, victory_point

    running_window.update_progress(40)
    print("正在處理history/state")

    #處理地塊(state)
    for path in root.path.avalible_path:
        try:

            #列出可以讀取的state檔案
            state_files = list(Path(path).joinpath("history/states").rglob("*txt"))

            #依序處理檔案
            for file in state_files:

                file_reading = file

                data = pdxread(file)[0]

                state_id = int(data["id"])

                #表示法可能分成合併型或並排型，同時會有在數量使用小數點的謎之行為要注意
                if data["resources"] is not None and data["resources"] != []:

                    #寫在一起
                    if isinstance(data["resources"],PDXstatement):
                        resources = { statement.keyword.lower(): int(float(statement.value)) for statement in data["resources"].value}

                    #並排分開
                    else:
                        resources = {statement.value[0].keyword.lower() : int(float(statement.value[0].value)) for statement in data["resources"]}
                else:
                    resources = None

                if data["history"]["buildings"] is not None:

                    if len(data["history"]["buildings"].value) != 0:

                        buildings = set()
                        
                        for statement in data["history"]["buildings"].value:

                            if not isinstance(statement.value,list):
                                buildings.add(Building(statement.keyword,statement.value))
                            
                            else:
                                province_buildings = set()
                                
                                for province_statement in statement.value:
                                    
                                    #考慮有些DLC才有的內容，如地標
                                    if not isinstance(province_statement.value,list):
                                        building_level = province_statement.value
                                    else:
                                        building_level = province_statement["level"]

                                    province_buildings.add(Building(name=province_statement.keyword,level=building_level))

                                root.map_data.province[int(statement.keyword)].buildings = province_buildings

                    else:
                        buildings = None
                else:
                    buildings = None
                
                if data["history"]["victory_points"] is not None:

                    if isinstance(data["history"]["victory_points"][0],list):
                        
                        for victory_point_data in data["history"]["victory_points"]:
                            province_id = victory_point_data[0]
                            victory_point_value = victory_point_data[1]
                            root.map_data.province[province_id].victory_point = victory_point_value
                    
                    else:
                        province_id = data["history"]["victory_points"][0]
                        victory_point_value = data["history"]["victory_points"][1]
                        root.map_data.province[province_id].victory_point = victory_point_value
                
                #參見history/states/190-Kurzeme.txt，他重複兩次category不知道在衝三小
                try:
                    state_category = data["state_category"].strip('"')
                except:
                    state_category = data["state_category"][-1].strip('"')

                #紀錄
                root.map_data.states[state_id] = State(id=state_id,
                                                       manpower=data["manpower"],
                                                       state_category=state_category,
                                                       provinces=data["provinces"],
                                                       owner=data["history"]["owner"],
                                                       local_supply=data["local_supplies"],
                                                       core=data["history"]["add_core_of"],
                                                       claim=data["history"]["add_claim_by"],
                                                       demilitarized_zone= True if data["history"]["set_demilitarized_zone"] == "yes" else False,
                                                       controller= data["history"]["controller"],
                                                       resources=resources,
                                                       buildings=buildings,
                                                       impassable=True if data["impassable"] == "yes" else False)

        except FileNotFoundError: pass
        except Exception as e:
            running_window.exception = f"讀取{file_reading}出現錯誤:{e}"
            print(fc.RED+tb.format_exc()+fc.CC)
            return
        
    #將province回來映射
    for state_id in root.map_data.states:
        for province_id in root.map_data.states[state_id].provinces:
            root.map_data.map_mapping.province_to_state[province_id] = state_id

    del path, state_files, file, file_reading, data, state_id, resources, buildings, statement, province_statement, building_level
    del victory_point_data, province_id, victory_point_value, state_category

    running_window.update_progress(90)

    #處理戰略區
    for path in root.path.avalible_path:

        #列出所有可以使用的檔案
        strategicregions_file_path = Path(path).joinpath("map/strategicregions")
        strategicregion_files = list(strategicregions_file_path.rglob("*txt"))

        try:

            #依序讀取檔案
            for file in strategicregion_files:

                file_reading = file
                data = pdxread(file)[0]
                strategicregion_id = int(data["id"])
                provinces = data["provinces"]
                name = data["name"].strip('"')
                naval_terrain = data["naval_terrain"]
                root.map_data.strategicregions[strategicregion_id] = StrategicRegion(strategicregion_id,provinces,name,naval_terrain=naval_terrain)

                #建立省分的逆向映射
                #留意: 原版的15 - Asia是空的
                if provinces is not None:
                    for province in provinces:
                        root.map_data.map_mapping.province_to_strategic[int(province)] = strategicregion_id

                        if running_window.is_cancel_task: return

        except Exception as e:
            running_window.exception = f"讀取{file_reading}出現錯誤:{e}"
            print(fc.RED+tb.format_exc()+fc.CC)
            return

    del path, strategicregions_file_path, strategicregion_files, file, file_reading, data, strategicregion_id, provinces, name, province

    running_window.update_progress(100)

def read_supply_node_file(file_path:str) -> set[int]:
    '''
    讀取補給基地所在的省份

    :param file_path: 檔案位置
    :return: 一串紀錄省分ID的列表
    '''
    with open(file_path,"r",encoding="utf-8") as file:
        result = list()
        for line in file:
            province = line.strip().split(" ")[1]
            result.append(int(province))
    
    return set(result)

def read_railway_file(file_path:str) -> tuple[Railway]:
    '''
    讀取鐵軌所在的省分及等級

    :param file_path: 檔案位置
    :return: 一串象徵每條鐵軌的列表
    '''
    with open(file_path,"r",encoding="utf-8") as file:
        result = list()
        for line in file:
            single_railway_data = line.strip().split(" ")
            railway_level = int(single_railway_data[0])

            converted = list()
            for province in single_railway_data[2:len(single_railway_data)]:
                converted.append(int(province))
            railway_provinces = converted[:]
            result.append(Railway(railway_level,railway_provinces))
    return tuple(result)

def read_country_tag_file(running_window:RunningWindow) -> None:
    '''
    讀取國家代碼
    '''
    running_window.update_progress(0)

    #找出實際使用的檔案

    using_country_tag_files:dict[str,str] = dict()

    for dir in root.path.avalible_path:

        country_tag_file_path = Path(dir + "/common/country_tags")
        country_tag_files = set(country_tag_file_path.rglob("*txt"))

        for file in country_tag_files:

            using_country_tag_files[file.stem] = file

    for index, country_tag_file in enumerate(using_country_tag_files.values()):

        country_tag_pdxscript = pdxread(country_tag_file)

        for statement in country_tag_pdxscript:

            root.path.country_tag[statement.keyword] = statement.value.strip('"')

            if running_window.is_cancel_task: return
        
        running_window.update_progress(int((index+1)/len(using_country_tag_files)*100))

def read_country_color(running_window:RunningWindow) -> None:
    """
    讀取國家顏色
    """

    import colorsys

    running_window.update_progress(0)
    country_color_file_path = Path(root.path.avalible_path[-1] + "/common/countries/colors.txt")

    color_data = ""

    # 將文件轉為一個字串，忽略註解行
    with open(country_color_file_path, "r", encoding="utf-8") as file:

        for line in file:

            if running_window.is_cancel_task: return
                
            # 移除註解
            line = re.sub(r"#.*", "", line).strip()

            if line: color_data += line + "\n"
                
    # 匹配 RGB 和 HSV 顏色數據
    pattern_rgb = re.compile(
        r"(\w+)\s*=\s*\{\s*color\s*=\s*(?i:rgb)\s*\{\s*(\d+)\s+(\d+)\s+(\d+)\s*\}", re.DOTALL
    )
    pattern_hsv = re.compile(
        r"(\w+)\s*=\s*\{\s*color\s*=\s*(?i:hsv)\s*\{\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\}", re.DOTALL
    )

    # 提取數據
    result_rgb = {match[1]: (int(match[2]), int(match[3]), int(match[4])) for match in pattern_rgb.finditer(color_data)}
    result_hsv = {match[1]: (float(match[2]),float(match[3]),float(match[4])) for match in pattern_hsv.finditer(color_data)}

    # HSV 轉換為 RGB
    for country_tag in result_hsv:
        h, s, v = result_hsv[country_tag]
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        result_hsv[country_tag] = (int(r * 255), int(g * 255), int(b * 255))

    # 合併結果
    root.map_data.color_mapping.country_color = result_rgb | result_hsv

    running_window.update_progress(100)

def create_province_map_image(running_window:RunningWindow) -> None:
    '''
    建立省分視圖
    '''
    running_window.update_progress(0)
    root.game_image.province_map = root.game_image.province_image.copy()

    running_window.update_progress(100)
        
def create_state_map_image(running_window:RunningWindow) -> None:
    '''
    建立地塊視圖
    '''
    running_window.update_progress(0)
    state_image = root.game_image.province_image.copy()
    w,h = state_image.size

    pixels = state_image.load()

    state_definition = dict()   #dict[list]，代表特定state id 之下的province顏色指派
    recorded_state = set()      #用於在後續檢查時確認是否已經有存在的地塊顏色

    #預先建立查詢表以加快速度
    color_to_state = dict()
    for color in root.map_data.color_mapping.avalible_color:
        state = State.from_province_id(Province.from_color(color).id)
        if state is not None:
            color_to_state[color] = state.id
        
        else:
            color_to_state[color] = None

    #對每個像素逐一檢查並修改
    for x in range(w):
        for y in range(h):
            
            #用戶中斷
            if running_window.is_cancel_task: return

            #獲取省分所在的地塊
            state = color_to_state[pixels[x,y]]

            #如果是海洋省份或未登記的省分，那就跳過該輪檢查
            if state is None:
                pixels[x,y] = (0,0,0)   #black
                continue
                
            #如果是尚未紀錄的省分
            if state not in recorded_state:
                state_definition[state] = pixels[x,y]
                recorded_state.add(state)
            
            #繪製
            pixels[x,y] = state_definition[state]

        running_window.update_progress(int((x/w)*100))
    
    root.game_image.state_map =  state_image

def create_strategic_map_image(running_window:RunningWindow) -> None:
    '''
    建立戰略區視圖
    '''
    running_window.update_progress(0)
    province_image = root.game_image.province_image.copy()
    w,h = province_image.size

    pixels = province_image.load()

    strategic_definition = dict() #dict[list]，代表特定strategic id 之下的province顏色指派
    recorded_strategic = set()

    #預先建立查詢表以加快速度
    color_to_strategic = dict()

    for color in root.map_data.color_mapping.avalible_color:

        try:
            color_to_strategic[color] = StrategicRegion.from_province_id(Province.from_color(color).id)
        except:
            running_window.exception = f"以下省分尚未指派戰略區，請在戰略區文件中添加該省分:{Province.from_color(color).id}"
            return

    #對每個像素逐一檢查並修改
    for x in range(w):
        for y in range(h):
            
            #用戶中斷
            if running_window.is_cancel_task: return

            #獲取省分所在的戰略區
            strategic_id = color_to_strategic[pixels[x,y]]
                
            #如果是尚未紀錄的省分
            if strategic_id not in recorded_strategic:
                strategic_definition[strategic_id] = pixels[x,y]
                recorded_strategic.add(strategic_id)
            
            pixels[x,y] = strategic_definition[strategic_id]

        running_window.update_progress(int((x/w)*100))
    
    root.game_image.strategic_map = province_image

def create_nation_map_image(running_window:RunningWindow) -> None:
    '''
    建立無條件時的政權地圖(有條件ex:比屬剛果)
    有條件的真的太麻煩，情況太多，不考慮處理。
    '''
    running_window.update_progress(0)
    nation_map_image = root.game_image.province_image.copy()

    pixels = nation_map_image.load()

    #建立查詢表
    get_country_color = dict()
    for color in root.map_data.color_mapping.avalible_color:

        try:
            get_country_color[color] = root.map_data.color_mapping.country_color[State.from_province_id(Province.from_color(color).id).owner]

        except AttributeError:
            get_country_color[color] = (0,0,0) #black
        
        except KeyError:
            get_country_color[color] = (25,25,25)   #gray
    
    #對每個像素進行繪製
    w,h = nation_map_image.size

    for x in range(w):
        for y in range(h):

            pixels[x,y] = get_country_color[pixels[x,y]]

            if running_window.is_cancel_task: return

        running_window.update_progress(int((x/w)*100))
    
    root.game_image.nation_map =  nation_map_image

def read_buildings_files(running_window:RunningWindow) -> None:
    '''
    讀取common/buildings
    '''
    running_window.update_progress(0)

    #收集檔案
    files:dict[str,str] = dict() # name: path

    for path in root.path.avalible_path:

        building_dir = Path(path).joinpath("common/buildings")
        building_files = list(building_dir.rglob("*.txt"))

        for building_file in building_files:
            files[building_file.name] = building_file
    
    #讀取
    for file in files.values():

        data = PDXstatement("file",pdxread(file))["buildings"].value

        for building_type_statement in data:

            statement:PDXstatement = building_type_statement

            name = statement.keyword
            icon_frame = statement["icon_frame"]
            
            level_cap_statement = statement["level_cap"]

            using_slot = "non-shared"

            if level_cap_statement["shares_slots"] is not None:using_slot = "shared"
                
            elif level_cap_statement["province_max"] is not None:using_slot = "provincial"
            
            if level_cap_statement["state_max"] is not None:
                max_level = level_cap_statement["state_max"]
            
            elif level_cap_statement["province_max"] is not None:
                max_level = level_cap_statement["province_max"]
            
            else:
                max_level = 15 # by hoi4 default
            
            if statement["only_costal"] is not None:    #原文如此
                only_coastal = True
            
            else:
                only_coastal = False
            
            if statement["disabled_in_dmz"] is not None:
                disabled_in_dmz = True
            
            else:
                disabled_in_dmz = False

            root.common_data.buildings[name] = BuildingData(name,icon_frame,using_slot,only_coastal,disabled_in_dmz,max_level)

