'''
root.py

繼承自ttk.Window的類型，儲存更多資訊如使用者變數與資訊
'''

from PIL import Image
import ttkbootstrap as ttk

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

class Root(ttk.Window):
    def __init__(self,*args,**kwargs) -> None:
        super().__init__(*args,**kwargs)

        self.hoi4path: str | None = None        #Heart of Iron IV 主遊戲的路徑
        self.modpath: str | None = None         #開發模組所在的路徑
        self.included_modpaths:list[str] = []   #引用的模組路徑
        self.avalible_path: list[str]           #整合本體遊戲、模組的路徑
        self.user_lang: str = "simp_chinese"    #模組開發語言(主要影響讀取本地化文件時的路徑)
        self.loc_data: dict                     #本地化文件

        #地圖資訊
        self.map_data:dict
        self.state_color:dict
        self.game_image:RootImage = RootImage()

        self.state_country_color_mapping:dict#state顏色對上國家TAG
        self.province_strategic_mapping:dict#province對上strategic_region

        #國家
        self.country_tag:dict               #國家TAG對上檔案名稱
        self.country_color:dict[tuple[int]]  #國家TAG對上顏色
        self.strategic_color:dict[tuple[int]] #戰略區對上顏色

        self.has_updated: bool = True           #是否完成資料更新I/O

root:Root = Root(title="鋼鐵雄心四模組工具",
                 themename="darkly",
                 size=(400,500))

def loc(key:str) -> str:
    '''
    獲取本地化字串
    '''
    try:
        return root.loc_data[key]
    
    except KeyError:
        return key