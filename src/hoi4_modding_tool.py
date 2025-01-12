'''
entry point of the software
'''

import ttkbootstrap as ttk
from tkinter import filedialog

from libs.root import Root
from libs.interface_io.read_loc_files import read_loc_files
from libs.interface_io.read_map_files import read_map_files
from libs.interface.character_creater import Character_creater
from libs.interface.progress_window import Progress_window

class App:
    def __init__(self) -> None:
        self.root = Root(title="鋼鐵雄心四模組工具",
                         themename="darkly",
                         size=(400,300))

        self.show_and_create_widget()
        self.update_task()
        self.root.mainloop()
    
    def show_and_create_widget(self) -> None:
        
        def character_btn_command() -> None:
            Character_creater(self.root)
            
        self.character_btn = ttk.Button(master=self.root,
                                        text="角色創建器",
                                        command=character_btn_command,
                                        state="disabled")
        self.character_btn.pack()

        def sel_dir_btn_command() -> None:
            resp = filedialog.askdirectory()
            if resp: self.root.hoi4path = resp
            self.root.has_updated = False

        sel_dir_btn = ttk.Button(master=self.root,
                                 text="選擇鋼四資料夾",
                                 command=sel_dir_btn_command)
        sel_dir_btn.pack(pady=20)

        def sel_mod_dir_btn_command() -> None:
            resp = filedialog.askdirectory()
            if resp: self.root.modpath = resp

        sel_mod_dir_btn = ttk.Button(master=self.root,
                                     text="選擇模組資料夾",
                                     command=sel_mod_dir_btn_command)
        sel_mod_dir_btn.pack(pady=20)
    
    def update_task(self) -> None:
        #檢查是否設定剛四資料夾
        if not self.root.has_updated:
            if self.root.hoi4path is not None:
                self.character_btn.config(state="normal")
                Progress_window(self.root,self.root,target=read_loc_files,output_container=self.root.loc_data,progress_msg="讀取本地化檔案")
                Progress_window(self.root,self.root,target=read_map_files,output_container=self.root.map_data,progress_msg="讀取地圖檔案")
                self.root.has_updated = True

        self.root.after(ms=100,func=self.update_task)
    