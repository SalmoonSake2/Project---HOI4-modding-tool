'''
get_province_from_color.py
從顏色獲取省分資訊
'''

from libs.root import Root

def get_province_from_color(root:Root,color:tuple) -> int:

    def find_province_by_rgb(r, g, b):
        match = (root.map_data["province"]['r'] == r) & \
                (root.map_data["province"]['g'] == g) & \
                (root.map_data["province"]['b'] == b)
        return root.map_data["province"][match][0]
    
    return find_province_by_rgb(*color)["id"]