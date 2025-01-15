'''
entry point of the software
'''

import ttkbootstrap as ttk
from tkinter import filedialog

from libs.root import Root
from libs.interface_io.read_loc_files import read_loc_files
from libs.interface_io.read_map_files import read_map_files
from libs.interface.character_creater import Character_creater
from libs.interface.map_view import Mapview
from libs.interface.running_window import RunningWindow

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
        self.character_btn.pack(pady=20)

        def map_view_btn_command() -> None:
            Mapview(self.root)

        self.map_view_btn = ttk.Button(master=self.root,
                                     text="地圖檢視器",
                                     command=map_view_btn_command,
                                     state="disabled")
        self.map_view_btn.pack(pady=20)

        def sel_dir_btn_command() -> None:
            resp = filedialog.askdirectory()
            if resp: 
                self.root.hoi4path = resp
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
        #檢查是否設定鋼四資料夾
        if not self.root.has_updated and self.root.hoi4path is not None:
            
            execute_list = list()
            args_list = list()
            callback_function_list = list()
            progress_msgs = list()

            def append_mission(mission,args,callback,msg):
                execute_list.append(mission)
                args_list.append(args)
                callback_function_list.append(callback)
                progress_msgs.append(msg)

            #本地化文檔
            def set_loc_data(x): self.root.loc_data = x
            append_mission(read_loc_files,(self.root,),set_loc_data,"建立本地化文檔")

            #地圖
            def set_map_data(x): self.root.map_data = x
            append_mission(read_map_files,(self.root,),set_map_data,"讀取地圖")

            #書籤

            #權力平衡

            #建築

            #腳色 @優先

            #持續性國策

            #國家文化、顏色 @優先

            #領導人、顧問特質 @優先

            #繼承國家代碼

            #國家代碼 @優先

            #決議 @優先

            #動態修飾

            #國家精神 @優先

            #意識形態

            #情報局

            #軍功組織

            #靜態修飾

            #名字

            #國策 @優先

            #on action

            #外交態度

            #間諜行動

            #突襲

            #資源

            #建築

            #編寫式內容

            #特殊項目

            #科技

            #科技共享

            #科技標籤

            #將領特質

            #勳章

            #編制標籤

            #編制

            #事件 @優先

            #歷史 @優先

            #介面與gfx @優先

            #音樂

            #頭像

            #按鈕設定
            def update_btn(running_window): 
                self.character_btn.config(state="normal")
                self.map_view_btn.config(state="normal")
            append_mission(update_btn,(),None,"更新畫面")

            RunningWindow(execute_list,args_list,callback_function_list,self.root,"執行中",progress_msgs)
            self.root.has_updated = True
            

        self.root.after(ms=100,func=self.update_task)
    