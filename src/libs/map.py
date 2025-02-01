'''
map.py

與地圖相關的事物

NOTICE: 更新任何東西時請確認是否連帶更新abstract_map.py
'''

from typing import Literal

from libs.pdxscript import PDXstatement
from libs.root import root

class Province:
    '''
    省分(province)相關
    '''
    def __init__(self,
                 id:int,
                 color:tuple[int,int,int],
                 terrain:Literal["unknown","lakes","forest","ocean","hills","plains","mountain","desert","marsh","urban","jungle"],
                 type:Literal["land","sea"],
                 coastal:bool,
                 continent:int) -> None:
        self.id = id                #省分ID
        self.color = color          #省分顏色
        self.terrain = terrain      #省分地形
        self.type = type            #省分海陸
        self.coastal = coastal      #省分臨海
        self.continent = continent  #省分大陸
        self.pos:tuple[int,int]  = None   #勝利點座標(西南原點)
        self.buildings:set[Building] = None    #建築
    
    @staticmethod
    def from_color(color:tuple[int,int,int]) -> 'Province':
        '''
        由給予的顏色獲取省分
        '''
        try:
            return root.map_data.province[root.map_data.color_mapping.province_id_from_color[color]]
        
        except KeyError:
            return None

class Adjacency:
    '''
    省分連結
    '''
    def __init__(self,
                 p1:int,
                 p2:int,
                 type:Literal["sea","impassable"] = "sea",
                 through:int | None = None,
                 pos1:tuple[int,int] | None = None,
                 pos2:tuple[int,int] | None = None,
                 rule:str = None) -> None:
        self.p1, self.p2 = p1, p2           #連結的兩個省份ID
        self.type = type                    #連結類型
        self.through = through              #通過的省分
        self.pos1, self.pos2 = pos1, pos2   #畫面起始與結束座標
        self.rule = rule                    #連結規則

class AdjacencyPassType:
    '''
    省分連結規則-通過類型
    '''
    def __init__(self,army:bool,navy:bool,submarine:bool,trade:bool) -> None:
        self.army = army
        self.navy = navy
        self.submarine = submarine
        self.trafe = trade

class AdjacencyRule:
    '''
    省分連結規則
    '''
    def __init__(self,
                 name:str,
                 contested:tuple[bool,bool,bool,bool],
                 enemy:tuple[bool,bool,bool,bool],
                 friend:tuple[bool,bool,bool,bool],
                 neutral:tuple[bool,bool,bool,bool],
                 required_provinces:set[int],
                 is_disabled:list[PDXstatement],
                 icon:int,
                 offset:tuple[int,int,int]) -> None:
        
        self.name = name                                #名稱代碼
        self.contested = AdjacencyPassType(*contested)  #敵對時的通過原則
        self.enemy = AdjacencyPassType(*enemy)          #戰爭時的通過原則
        self.friend = AdjacencyPassType(*friend)        #友好時的通過原則
        self.neutral = AdjacencyPassType(*neutral)      #中立時的通過原則
        self.required_provinces = required_provinces    #控制的省份
        self.is_disabled = is_disabled                  #禁用的原則
        self.icon_province = icon                       #圖示所在的省份ID
        self.offset = offset                            #圖示偏移的量

class Railway:
    '''
    鐵路
    '''
    def __init__(self,level:int,provinces:tuple[int]) -> None:
        self.level = level
        self.provinces = provinces

class Building:
    '''
    建築
    '''
    def __init__(self,
                 name:Literal["infrastructure",
                              "arms_factory",
                              "industrial_complex",
                              "air_base",
                              "naval_facility",
                              "naval_base",
                              "bunker",
                              "coastal_bunker",
                              "stronghold_network",
                              "dockyard",
                              "anti_air_building",
                              "synthetic_refinery",
                              "fuel_silo",
                              "radar_station",
                              "mega_gun_emplacement",
                              "rocket_site",
                              "nuclear_reactor",
                              "nuclear_reactor_heavy_water",
                              "commercial_nuclear_reactor",
                              "nuclear_facility",
                              "air_facility",
                              "land_facility",
                              "dam",
                              "...others"],
                 level:int) -> None:
        self.name = name
        self.level = level

class State:
    '''
    地塊(state)相關
    '''
    def __init__(self,
                 id:int,
                 manpower:int,
                 state_category:Literal["wasteland","enclave","tiny_island","pastoral","small_island","rural","town","large_town","city","large_city","metropolis","megalopolis"],                      
                 owner:str,
                 provinces:tuple[int],
                 local_supply:float = 0,
                 resources:dict[str,int] = None,
                 victory_points:dict[int,int] = None,
                 buildings:set[Building] = None,
                 core:set[str] = None,
                 claim:set[str] = None,
                 impassable:bool = False,
                 demilitarized_zone:bool = False,
                 controller:str = None) -> None:
        
        self.id = id
        self.manpower = manpower
        self.state_category = state_category
        self.owner = owner
        self.provinces = provinces
        self.local_supply = local_supply
        self.resources = resources
        self.victory_points = victory_points
        self.buildings = buildings
        self.core = core
        self.claim = claim
        self.impassable = impassable
        self.controller = controller
        self.demilitarized_zone = demilitarized_zone
    
    @staticmethod
    def from_province_id(province_id:int) -> 'State':
        '''
        由省分ID獲得地塊資訊
        '''
        try:
            return root.map_data.states[root.map_data.map_mapping.province_to_state[province_id]]
        except KeyError:
            return None
    
class StrategicRegion:
    '''
    戰略區
    '''
    def __init__(self,id:int,provinces:tuple[int],name:str) -> None:
        self.id = id
        self.name = name
        self.provinces = provinces
    
    @staticmethod
    def from_province_id(id:int) -> 'StrategicRegion':
        '''
        由省分ID獲得戰略區資料
        '''
        return root.map_data.strategicregions[root.map_data.map_mapping.province_to_strategic[id]]
