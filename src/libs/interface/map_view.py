'''
map_view.py
'''

import ttkbootstrap as ttk

from libs.root import Root

class Mapview:

    def __init__(self,root:Root) -> None:
        self.root = root
        self.show_and_create_widget()
    
    def show_and_create_widget(self) -> None:
        
        toplevel = ttk.Toplevel(title="地圖檢視器",
                            size=(750,570),
                            transient=self.root)
        
        #檢視province, state, strategic region
        #縮放
        #繪製省分、河流、高度圖、地形外觀、樹種、設定資料
        #導入n貼圖、unitstack、buildings
        #繪製鐵路、補給基地
