'''
root.py

繼承自ttk.Window的類型，儲存更多資訊如使用者變數與資訊

更新時請檢察cache_reader.py是否正常修改
'''

from PIL import Image
import ttkbootstrap as ttk

from libs.abstract.abstract_map import *
from libs.misc.buildings import BuildingData

class RootImage:
    '''
    圖像儲存區
    '''
    def __init__(self) -> None:
        self.province_image:Image.Image         #province.bmp
        self.terrain_image:Image.Image          #terrain.bmp
        self.heightmap_image:Image.Image        #heightmap.bmp
        self.rivers_image:Image.Image           #rivers.bmp

        self.province_map:Image.Image           #省分視圖
        self.state_map:Image.Image              #地塊視圖
        self.strategic_map:Image.Image          #戰略區視圖
        self.nation_map:Image.Image             #政權視圖

class ColorMapping:
    '''
    顏色指派儲存區
    '''
    def __init__(self) -> None:
        self.avalible_color:set[tuple[int,int,int]] = set()         #省分顏色集合
        self.province_id_from_color:dict[tuple,int] = dict()        #由顏色獲取省分id
        self.country_color: dict[str,tuple[int,int,int]] = dict()   #國家TAG對上顏色

class MapMapping:
    '''
    地圖相關的儲存區
    '''
    def __init__(self) -> None:
        self.province_to_state:dict[int,int] = dict()           #省分ID對上地塊ID
        self.province_to_strategic:dict[int,int] = dict()       #省分ID對上戰略區ID

class Mapdata:
    '''
    地圖資料儲存區
    '''
    def __init__(self) -> None:
        self.province:dict[int,Province] = dict()               #省分資料
        self.adjacencies: set[Adjacency] = set()                #省分連結
        self.adjacency_rules: dict[str,AdjacencyRule] = dict()  #省分連結規則，以代號為key找到其規則
        self.continents: dict[int,str] = dict()                 #大陸指派，以id為key找到其字串
        self.supply_nodes: set[int] = set()                     #補給基地的所在省分
        self.railways: tuple[Railway]                           #鐵路
        self.strategicregions:dict[int,StrategicRegion] = dict()   #map/strategicregions
        self.states:dict[int,State] = dict()                    #地塊

        self.map_mapping:MapMapping = MapMapping()              #地圖元件映射
        self.color_mapping:ColorMapping = ColorMapping()        #顏色指派

class Rootpath:
    '''
    路徑儲存區
    '''
    def __init__(self) -> None:
        self.hoi4path:str = None                #Heart of Iron IV 主遊戲的路徑
        self.modpath:str = None                 #開發模組所在的路徑
        self.included_modpaths:list[str] = []   #引用的模組路徑
        self.avalible_path: list[str]           #整合本體遊戲、模組的路徑

        self.country_tag:dict = dict()          #國家TAG對上檔案名稱

class CommonData:
    '''
    難以歸類的遊戲資料
    '''
    def __init__(self):
        self.buildings:dict[str,BuildingData] = dict()  #建築屬性

class Root(ttk.Window):
    def __init__(self,*args,**kwargs) -> None:
        super().__init__(*args,**kwargs)
        self.mod_lang: str = "simp_chinese"         #模組開發語言(主要影響讀取本地化文件時的路徑)
        self.using_cache:bool = True                #使用快取建立檔案
        self.game_loc: dict = dict()                #本地化文件
        self.path:Rootpath = Rootpath()             #路徑
        self.map_data:Mapdata = Mapdata()           #地圖資訊
        self.common_data:CommonData = CommonData()  #難以歸類的遊戲資料
        self.game_image:RootImage = RootImage()     #圖像

root:Root = Root(title="鋼鐵雄心四模組工具",
                 themename="darkly",
                 size=(1000,600))