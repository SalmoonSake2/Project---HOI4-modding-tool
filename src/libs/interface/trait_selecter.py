'''
trait_selecter.py
'''

import ttkbootstrap as ttk

from libs.root import Root

class Trait_selecter:
    '''
    特質選擇器，從檔案中尋找特質並顯示
    '''
    def __init__(self,prev,root:Root) -> None:
        self.root = root
        self.prev = prev
        self.show_and_create_widget()
    
    def show_and_create_widget(self) -> None:
        toplevel = ttk.Toplevel(title="特質選擇器",
                            size=(500,300),
                            transient=self.prev,
                            resizable=(False,False))