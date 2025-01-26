'''
map.py

與地圖相關的事物
'''

from libs.root import root

class Province:
    '''
    省分(province)相關
    '''
    def __init__(self,id,color,terrain,type,coastal,continent) -> None:
        self.id = id
        self.color = color
        self.terrain = terrain
        self.type = type
        self.coastal = coastal
        self.continent = continent
    
    @staticmethod
    def from_color(color:tuple) -> 'Province':
        '''
        從給予的顏色tuple獲取省分

        :param color: 顏色(RGB)的tuple
        '''
        def find_id_by_rgb(r, g, b):
            match = (root.map_data["province"]['r'] == r) & \
                    (root.map_data["province"]['g'] == g) & \
                    (root.map_data["province"]['b'] == b)
            return root.map_data["province"][match][0]
        
        province_id = find_id_by_rgb(*color)["id"]

        province_data = root.map_data["province"][root.map_data["province"]["id"] == province_id][0]
        return Province(province_data["id"],
                        color,
                        province_data["category"],
                        province_data["type"],
                        province_data["coastal"],
                        province_data["continent"])

class State:
    '''
    地塊(state)相關
    '''
    def __init__(self,id) -> None:
        self.id = id
    
    @staticmethod
    def get_state_from_id(id:int) -> 'State':
        '''
        由已知ID獲取地塊資料
        '''
        return State(id)
    
    @staticmethod
    def from_province(province:Province) -> 'State':
        '''
        由已知的省分獲取地塊資料

        :param province: 省分
        '''

        for state_id in root.map_data["state-province"]:
            if province.id in root.map_data["state-province"][state_id]:
                return State.get_state_from_id(state_id)
