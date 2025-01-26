'''
reader.py
讀取文檔相關的操作
'''
import colorsys
import re

import numpy as np
from pathlib import Path
from PIL import Image

from libs.enums import *
from libs.interface.running_window import RunningWindow
from libs.map import Province, State
from libs.pdxscript import read as pdxread
from libs.pdxscript import PDXstatement
from libs.root import root

def get_mod_name(path:str) -> str:
    '''
    獲取模組名稱

    :param path: 模組資料夾所在路徑
    '''

    try:
        mod_name = PDXstatement("mod",pdxread(path+"/descriptor.mod"))["name"].strip('"')
        mod_version =  PDXstatement("mod",pdxread(path+"/descriptor.mod"))["version"].strip('"')
    except:
        raise Exception("模組讀取失敗")
    
    return mod_name+"("+mod_version+")"
    
def integrate_path(running_window:RunningWindow) -> None:
    '''
    整合本體遊戲、模組的路徑
    '''
    avalible_path = [root.hoi4path]
    avalible_path.extend(root.included_modpaths)
    if root.modpath is not None:
        avalible_path.extend([root.modpath])
    root.avalible_path = avalible_path

def check_path_avalibility(running_window:RunningWindow) -> None:
    '''
    確認路徑有效性
    '''

    #檢驗路徑是否存在
    if root.hoi4path is None:
        running_window.exception = "The game path is not given!"
        return
    
    #確認遊戲路徑是否正常
    if not Path(root.hoi4path).joinpath("hoi4.exe").exists():
        running_window.exception = "Invalid path selection for Heart of Iron IV"
        return
    
    #確認模組路徑是否正常
    if root.modpath is not None:
        if not Path(root.modpath).joinpath("descriptor.mod").exists():
            running_window.exception = f"Invalid path selection for mod included: {path}"
            return

    for path in root.included_modpaths:
        if not Path(path).joinpath("descriptor.mod").exists():
            running_window.exception = f"Invalid path selection for mod included: {path}"
            return
    
def read_loc_files(running_window:RunningWindow) -> None:
    '''
    讀取本地化文件
    '''

    #儲存輸出結果的字典
    running_window.localization_data = dict() 

    #讀取包括模組的每一個本地化文件路徑
    for loc_dir in root.avalible_path:

        loc_file_path = Path(loc_dir).joinpath("localisation")

        #找出該路徑下的所有本地化文件
        loc_files_en = list(loc_file_path.rglob(f"*l_english.yml"))
        loc_files = list(loc_file_path.rglob(f"*l_{root.user_lang}.yml"))
        loc_files_en.extend(loc_files)
    
        #依序處理每個yml檔
        for loc_file in loc_files_en:
            read_loc_file(running_window,loc_file)
            if running_window.is_cancel_task:
                break
        
        if running_window.is_cancel_task:
            return
    
    #輸出檔案
    root.loc_data = running_window.localization_data

def read_loc_file(running_window:RunningWindow,loc_file:str) -> None:
    '''
    讀取`loc_file`的本地化文檔

    :param running_window: 引用的框架
    :param loc_file: 本地化文檔的路徑
    '''
    pattern = r'(\w+):\s*\d*?\s*"([^"]+)"'#形如 keyword : "value"的特徵。
    try:
        with open(file=loc_file,mode="r",encoding="utf-8-sig") as file:
            for line in file:
                match = re.search(pattern, line.strip())
                if match:
                    key, value = match.groups()
                    running_window.localization_data[key] = value

                if running_window.is_cancel_task:
                    break
    except FileNotFoundError as e:
        running_window.exception = e

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

def read_map_files(running_window:RunningWindow) -> None:
    '''
    讀取地圖檔案，相關技術細節可以參閱\n
    https://hoi4.paradoxwikis.com/Map_modding#Provinces

    :param root: 根視窗
    '''

    running_window.update_progress(0)

    for path in root.avalible_path:
        try: root.game_image.province_image = Image.open(path + "/map/provinces.bmp")
        except FileNotFoundError: pass
        except Exception as e:
            running_window.exception = f"Something went wrong when handling file:{path},{e}"
    
    for path in root.avalible_path:
        try: root.game_image.terrain_image = Image.open(path +"/map/terrain.bmp")
        except FileNotFoundError: pass
        except Exception as e:
            running_window.exception = f"Something went wrong when handling file:{path},{e}"
    
    for path in root.avalible_path:
        try: root.game_image.heightmap_image = Image.open(path +"/map/heightmap.bmp")
        except FileNotFoundError: pass
        except Exception as e:
            running_window.exception = f"Something went wrong when handling file:{path},{e}"

    for path in root.avalible_path:
        try: root.game_image.rivers_image = Image.open(path +"/map/rivers.bmp")
        except FileNotFoundError: pass
        except Exception as e:
            running_window.exception = f"Something went wrong when handling file:{path},{e}"

    province_definitions_csv_column_names = ("id","r","g","b","type","coastal","category","continent")

    for path in root.avalible_path:
        try:
            province_definitions = np.genfromtxt(Path(path).joinpath("map").joinpath("definition.csv"),
                                                 delimiter=";",
                                                 dtype=None,
                                                 encoding="utf-8",
                                                 names=province_definitions_csv_column_names)
        except FileNotFoundError: pass
        except Exception as e:
            running_window.exception = f"Something went wrong when handling file:{path},{e}"
    
    for path in root.avalible_path:
        try:
            adjacencies_data = np.genfromtxt(Path(path).joinpath("map").joinpath("adjacencies.csv"),
                                             delimiter=";",
                                             dtype=None,
                                             encoding="utf-8",
                                             invalid_raise=False,
                                             names=True)
        except FileNotFoundError: pass
        except Exception as e:
            running_window.exception = f"Something went wrong when handling file:{path},{e}"
    
    for path in root.avalible_path:
        try: adjacency_rules_data = pdxread(Path(path).joinpath("map").joinpath("adjacency_rules.txt"))
        except FileNotFoundError: pass
        except Exception as e:
            running_window.exception = f"Something went wrong when handling file:{path},{e}"

    for path in root.avalible_path:
        try: continent_data = pdxread(Path(path).joinpath("map").joinpath("continent.txt"))
        except FileNotFoundError: pass
        except Exception as e:
            running_window.exception = f"Something went wrong when handling file:{path},{e}"

    for path in root.avalible_path:
        try: seasons_data = pdxread(Path(path).joinpath("map").joinpath("seasons.txt"))
        except FileNotFoundError: pass
        except Exception as e:
            running_window.exception = f"Something went wrong when handling file:{path},{e}"

    for path in root.avalible_path:
        try: supply_nodes_data = read_supply_node_file(Path(path).joinpath("map").joinpath("supply_nodes.txt"))
        except FileNotFoundError: pass
        except Exception as e:
            running_window.exception = f"Something went wrong when handling file:{path},{e}"

    for path in root.avalible_path:
        try: railway_data = read_railway_file(Path(path).joinpath("map").joinpath("railways.txt"))
        except FileNotFoundError: pass
        except Exception as e:
            running_window.exception = f"Something went wrong when handling file:{path},{e}"
    
    for path in root.avalible_path:
        try:
            unitstack_column_names = ("id","type","x","y","z","rotation","offset")
            unitstacks_data = np.genfromtxt(Path(path).joinpath("map").joinpath("unitstacks.txt"),
                                            delimiter=";",
                                            dtype=None,
                                            encoding="utf-8",
                                            invalid_raise=False,
                                            names=unitstack_column_names)
        except FileNotFoundError: pass
        except Exception as e:
            running_window.exception = f"Something went wrong when handling file:{path},{e}"
    
    running_window.update_progress(30)

    ###############################################################################################################################################

    for path in root.avalible_path:
        try:
            state_data = dict()
            state_province_mapping = dict()
            state_files = list(Path(path).joinpath("history/states").rglob("*txt"))

            file_reading = None
            for file in state_files:

                file_reading = file
                data = pdxread(file)

                state_id = int(data[0]["id"])

                #列出其擁有的所有省分
                provinces = data[0]["provinces"]
                state_province_mapping[state_id] = provinces
                
                state_data[state_id] = data
        
        except Exception as e:
            running_window.exception = f"讀取{file_reading}出現錯誤:{e}"
            return

    for path in root.avalible_path:
        strategicregions_file_path = Path(path).joinpath("map/strategicregions")
        try:
            strategicregion_data = dict()
            strategicregion_files = list(strategicregions_file_path.rglob("*txt"))

            for file in strategicregion_files:

                file_reading = file
                data = pdxread(file)
                strategicregion_id = int(data[0]["id"])
                strategicregion_data[strategicregion_id] = data

        except Exception as e:
            running_window.exception = f"讀取{file_reading}出現錯誤:{e}"
            return
        
        root.map_data  = {"province":province_definitions,
                        "adjacency":adjacencies_data,
                        "adjacency_rule":adjacency_rules_data,
                        "continent":continent_data,
                        "season":seasons_data,
                        "supply_node":supply_nodes_data,
                        "railway":railway_data,
                        "state": state_data,
                        "unitstack": unitstacks_data,
                        "state-province": state_province_mapping,
                        "strategicregion":strategicregion_data}

def read_country_tag_file(running_window:RunningWindow) -> None:
    '''
    讀取國家代碼
    '''
    running_window.update_progress(0)

    #找出實際使用的檔案
    using_country_tag_files:dict[str,str] = dict()
    for dir in root.avalible_path:
        country_tag_file_path = Path(dir + "/common/country_tags")
        country_tag_files = set(country_tag_file_path.rglob("*txt"))
        for file in country_tag_files:
            using_country_tag_files[file.stem] = file

    country_tags = dict()
    for file_name, country_tag_file in using_country_tag_files.items():
        country_tag_pdxscript = pdxread(country_tag_file)
        for statement in country_tag_pdxscript:
            country_tags[statement.keyword] = statement.value.strip('"')
            if running_window.is_cancel_task: return
    
    root.country_tag =  country_tags

def read_country_color(running_window:RunningWindow) -> None:
    """
    讀取國家顏色
    """
    running_window.update_progress(0)
    country_color_file_path = Path(root.avalible_path[-1] + "/common/countries/colors.txt")

    color_data = ""

    # 讀取文件，忽略註解行
    with open(country_color_file_path, "r", encoding="utf-8") as file:
        for line in file:
            if running_window.is_cancel_task:
                return
            # 移除註解
            line = re.sub(r"#.*", "", line).strip()
            if line:  # 忽略空行
                color_data += line + "\n"

    # 匹配 RGB 和 HSV 顏色數據
    pattern_rgb = re.compile(
        r"(\w+)\s*=\s*\{\s*color\s*=\s*rgb\s*\{\s*(\d+)\s+(\d+)\s+(\d+)\s*\}", re.DOTALL
    )
    pattern_hsv = re.compile(
        r"(\w+)\s*=\s*\{\s*color\s*=\s*hsv\s*\{\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\}", re.DOTALL
    )

    # 提取數據
    result_rgb = {
        match[1]: (int(match[2]), int(match[3]), int(match[4]))
        for match in pattern_rgb.finditer(color_data)
    }
    result_hsv = {
        match[1]: (
            float(match[2]),
            float(match[3]),
            float(match[4]),
        )
        for match in pattern_hsv.finditer(color_data)
    }

    # HSV 轉換為 RGB
    for country_tag in result_hsv:
        h, s, v = result_hsv[country_tag]
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        result_hsv[country_tag] = (int(r * 255), int(g * 255), int(b * 255))

    # 合併結果
    root.country_color = {**result_rgb, **result_hsv}

def create_province_map_image(running_window:RunningWindow) -> None:
    '''
    建立省分視圖
    '''
    running_window.update_progress(0)

    #廢案，標註省分中心
    # pixels = province_image.load()
    # w,h = province_image.size

    # def get_vic_pos(province_id:int) -> tuple[int,int]:
    #     match = (root.map_data["unitstack"]["id"] == province_id ) &\
    #             (root.map_data["unitstack"]["type"] == 38)
    #     try:
    #         data = root.map_data["unitstack"][match][0]
    #         return (data["x"],data["z"])
    #     except:
    #         return (0,0)

    # for counter, province in enumerate(root.map_data["province"]):
    #     vic_x, vic_y = get_vic_pos(province["id"])
    #     vic_x = vic_x +1
    #     vic_y = h - vic_y -1
    #     try:
    #         pixels[vic_x,vic_y] = (255,255,255)
    #     except:
    #         raise Exception(f"{vic_x,vic_y}")
    #     running_window.progress_var = int((counter/len(root.map_data["province"]))*100)
    
    root.game_image.province_map = root.game_image.province_image.copy()

    running_window.update_progress(100)
        
def create_state_map_image(running_window:RunningWindow) -> None:
    '''
    建立地塊視圖
    '''
    running_window.update_progress(0)
    province_image = root.game_image.province_image.copy()
    w,h = province_image.size

    pixels = province_image.load()

    state_definition = dict() #dict[list]，代表特定state id 之下的province顏色指派
    recorded_state = set()

    #預先建立查詢表以加快速度
    avalible_color = set()

    for province_data in root.map_data["province"]:
        r = province_data["r"]
        g = province_data["g"]
        b = province_data["b"]
        avalible_color.add((r,g,b))

    color_to_state = {color : State.from_province(Province.from_color(color)) for color in avalible_color}

    #對每個像素逐一檢查並修改
    for x in range(w):
        for y in range(h):
            
            #用戶中斷
            if running_window.is_cancel_task: return

            #獲取省分所在的地塊
            state = color_to_state[pixels[x,y]]

            #如果是海洋省份或未登記的省分，那就跳過該輪檢查
            if state is None: continue
                
            #如果是尚未紀錄的省分
            if state.id not in recorded_state:
                state_definition[state.id] = pixels[x,y]
                recorded_state.add(state.id)
            
            #繪製
            pixels[x,y] = state_definition[state.id]

        running_window.update_progress(int((x/w)*100))
    
    root.state_color = state_definition
    
    root.game_image.state_map =  province_image

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
    province_strategic_mapping = dict()

    #預先建立查詢表以加快速度
    avalible_color = set()

    for province_data in root.map_data["province"]:
        r = province_data["r"]
        g = province_data["g"]
        b = province_data["b"]
        avalible_color.add((r,g,b))
    
    #依序找出其所隸屬的省分
    for strategicregion_id in root.map_data["strategicregion"]:
        provinces = root.map_data["strategicregion"][strategicregion_id][0]["provinces"]
        for province in provinces:
            province_strategic_mapping[province] = strategicregion_id
    
    root.province_strategic_mapping = province_strategic_mapping

    color_to_strategic = dict()
    for color in avalible_color:
        try:
            color_to_strategic[color] = province_strategic_mapping[Province.from_color(color).id]
        except:
            ...

    #對每個像素逐一檢查並修改
    for x in range(w):
        for y in range(h):
            
            #用戶中斷
            if running_window.is_cancel_task: return

            #獲取省分所在的戰略區
            strategic_id = color_to_strategic[pixels[x,y]]

            #如果是海洋省份或未登記的省分，那就跳過該輪檢查
            if strategic_id is None: continue
                
            #如果是尚未紀錄的省分
            if strategic_id not in recorded_strategic:
                strategic_definition[strategic_id] = pixels[x,y]
                recorded_strategic.add(strategic_id)
            
            #繪製
            pixels[x,y] = strategic_definition[strategic_id]

        running_window.update_progress(int((x/w)*100))
    
    root.strategic_color = strategic_definition
    
    root.game_image.strategic_map = province_image

def create_nation_map_image(running_window:RunningWindow) -> None:
    '''
    建立無條件時的政權地圖(有條件ex:比屬剛果)
    '''
    running_window.update_progress(0)
    nation_map_image = root.game_image.state_map.copy()

    pixels = nation_map_image.load()

    #建立state顏色對國家顏色的配對
    state_country_color_mapping = dict()
    root.state_country_color_mapping = dict()

    #逐一輸入state可能的顏色進行計算
    for state_id in root.state_color:
        state_history_data = PDXstatement("history",root.map_data["state"][state_id][0]["history"])
        country_tag = state_history_data["owner"]
        try:
            country_color = root.country_color[country_tag]
        except:
            country_color = (20,20,20)
        state_country_color_mapping[root.state_color[state_id]] = country_color
        root.state_country_color_mapping[root.state_color[state_id]] = country_tag
    
    
    #對每個像素進行繪製
    w,h = nation_map_image.size

    for x in range(w):
        for y in range(h):
            try:
                pixels[x,y] = state_country_color_mapping[pixels[x,y]]
            except KeyError:
                pixels[x,y] = (0,0,0)

            if running_window.is_cancel_task: return

        running_window.update_progress(int((x/w)*100))
    
    root.game_image.nation_map =  nation_map_image