'''
root.py

繼承自ttk.Window的類型，儲存更多資訊如使用者變數與資訊
'''

import ttkbootstrap as ttk

class Root(ttk.Window):
    def __init__(self,*args,**kwargs) -> None:
        super().__init__(*args,**kwargs)

        #Heart of Iron IV 主遊戲的路徑
        self.hoi4path: str | None = None

        #模組所在的路徑
        self.modpath: str | None = None

        #模組開發語言
        self.user_lang: str = "simp_chinese"

        #本地化文件
        self.loc_data: dict = None

        #地圖資訊
        self.map_data:dict = None

        #是否更新介面
        self.has_updated: bool = True