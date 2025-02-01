'''
abstract_map.py

抽象map.py物件
'''

from typing import Literal

from libs.pdxscript import PDXstatement

class Province:
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
        self.victory_point:int = None   #勝利點價值
        self.pos:tuple[int,int]     #勝利點座標(西南原點)
        self.buildings:set[Building]    #建築
    
    @staticmethod
    def from_color(color:tuple[int,int,int]) -> 'Province':...

class Adjacency:
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
    def __init__(self,army:bool,navy:bool,submarine:bool,trade:bool) -> None:
        self.army = army
        self.navy = navy
        self.submarine = submarine
        self.trafe = trade

class AdjacencyRule:
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
    def __init__(self,level:int,provinces:tuple[int]) -> None:
        self.level = level
        self.provinces = provinces

class Building:
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
    def __init__(self,
                 id:int,
                 manpower:int,
                 state_category:Literal["wasteland","enclave","tiny_island","pastoral","small_island","rural","town","large_town","city","large_city","metropolis","megalopolis"],                      
                 owner:str,
                 provinces:tuple[int],
                 local_supply:float = 0,
                 resources:dict[str,int] = None,
                 buildings:set[Building] = None,
                 core:set[str] = None,
                 claim:set[str] = None,
                 impassable:bool = False,
                 controller:str = None) -> None:
        
        self.id = id
        self.manpower = manpower
        self.state_category = state_category
        self.owner = owner
        self.provinces = provinces
        self.local_supply = local_supply
        self.resources = resources
        self.buildings = buildings
        self.core = core
        self.claim = claim
        self.impassable = impassable
        self.controller = controller
    
    @staticmethod
    def from_province_id(province_id:int) -> 'State':...

class StrategicRegion:
    def __init__(self,id:int,provinces:tuple[int],name:str) -> None:
        self.id = id
        self.name = name
        self.provinces = provinces
    
    @staticmethod
    def from_province(id:int) -> 'StrategicRegion':...