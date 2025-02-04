'''
buildings.py

遊戲建築的資料儲存

P:不要與Building (mapdata) 混淆
'''

from typing import Literal

class BuildingData:
    '''
    建築資料儲存的地方
    '''
    def __init__(self,
                 name:str,
                 icon_frame:int = 22,
                 using_slot:Literal["shared","non-shared","provincial"] = "non-shared",
                 only_coastal:bool = False,
                 disabled_in_dmz:bool = False,
                 max_level:int = 15) -> None:
        self.name = name
        self.icon_frame = icon_frame
        self.using_slot = using_slot
        self.only_coastal = only_coastal
        self.disabled_in_dmz = disabled_in_dmz
        self.max_level = max_level
        
