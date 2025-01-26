'''
hoi4_modding_tool.py

程式的本體
'''

from tkinter import filedialog

from pathlib import Path
import ttkbootstrap as ttk

from libs.interface.character_creater import Character_creater
from libs.interface.map_view import Mapview
from libs.interface.running_window import RunningWindow
from libs.reader import *
from libs.root import Root

class App:
    def __init__(self) -> None:
        self.root = Root(title="鋼鐵雄心四模組工具",
                         themename="darkly",
                         size=(400,300))

        self.show_and_create_widget()
        self.find_hoi4_path()
        self.update_task()
        self.root.mainloop()
    
    def find_hoi4_path(self) -> None:
        if Path("C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV").exists():
            self.root.hoi4path = "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV"
            self.root.first_try_hoi4_path = True
            self.root.has_updated = False

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

        self.sel_dir_btn = ttk.Button(master=self.root,
                                 text="選擇鋼四資料夾",
                                 command=sel_dir_btn_command)
        self.sel_dir_btn.pack(pady=20)

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

            append_mission(read_loc_files,(self.root,),None,"讀取localisation")
            append_mission(read_map_files,(self.root,),None,"讀取map與history/states")
            append_mission(read_country_tag_file,(self.root,),None,"讀取common/country_tags")
            append_mission(read_country_color,(self.root,),None,"讀取common/countries")
            append_mission(create_province_map_image,(self.root,),None,"繪製省分地圖")
            append_mission(create_state_map_image,(self.root,),None,"繪製地塊地圖")
            append_mission(create_strategic_map_image,(self.root,),None,"繪製戰略區地圖")
            append_mission(create_nation_map_image,(self.root,),None,"繪製政權地圖")

            def update_btn(running_window): 
                '''
                確保在任務完成後才更新畫面
                '''
                self.character_btn.config(state="normal")
                self.map_view_btn.config(state="normal")
                self.sel_dir_btn.config(state="disabled")
            append_mission(update_btn,(),None,"更新畫面")

            RunningWindow(execute_list,args_list,callback_function_list,self.root,"執行中",progress_msgs)
            self.root.has_updated = True
            
        self.root.after(ms=100,func=self.update_task)
    