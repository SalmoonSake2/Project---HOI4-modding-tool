'''
trait_creater.py
'''

import ttkbootstrap as ttk

class Trait_creater:
    '''
    特質創建器
    '''
    def __init__(self,root,prev) -> None:
        self.root = root
        self.prev - prev
        self.show_and_create_widget()
    
    def show_and_create_widget(self) -> None:
        toplevel = ttk.Toplevel(title="特質創建器",
                            size=(500,300),
                            transient=self.prev,
                            resizable=(False,False))