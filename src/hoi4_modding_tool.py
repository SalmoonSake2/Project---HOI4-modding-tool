'''
hoi4_modding_tool.py

程式的本體
'''

from tkinter import filedialog

from pathlib import Path
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox as msg

from libs.interface.character_creater import Character_creater
from libs.interface.map_view import Mapview
from libs.interface.running_window import RunningWindow
from libs.cache_reader import save_cache, load_cache
from libs.reader import *
from libs.root import root

class App:
    def __init__(self) -> None:
        self.show_and_create_widget()
        self.find_hoi4_path()
        self.update_task()
        root.mainloop()
    
    def find_hoi4_path(self) -> None:
        common_game_path = "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV"
        root.path.hoi4path = common_game_path if Path(common_game_path).exists() else None

    def show_and_create_widget(self) -> None:
        
        def character_btn_command(): Character_creater(root)
            
        self.character_btn = ttk.Button(master=root,
                                        text="角色創建器",
                                        command=character_btn_command,
                                        state="disabled")
        self.character_btn.pack(pady=20)

        def map_view_btn_command(): Mapview(root)
            
        self.map_view_btn = ttk.Button(master=root,
                                       text="地圖檢視器",
                                       command=map_view_btn_command,
                                       state="disabled")
        self.map_view_btn.pack(pady=20)

        def sel_dir_btn_command():
            resp = filedialog.askdirectory()
            if resp: 
                root.path.hoi4path = resp

        self.sel_dir_btn = ttk.Button(master=root,
                                 text="遊戲資料夾",
                                 command=sel_dir_btn_command)
        self.sel_dir_btn.pack(pady=20)

        def sel_mod_dir_btn_command():
            resp = filedialog.askdirectory()
            if resp: root.path.modpath = resp

        sel_mod_dir_btn = ttk.Button(master=root,
                                     text="模組資料夾",
                                     command=sel_mod_dir_btn_command)
        sel_mod_dir_btn.pack(pady=20)

        def included_mod_dir_btn_command():
            resp = filedialog.askdirectory()
            if resp: root.path.included_modpaths.append(resp)
            name_list = list()
            
            for path in root.path.included_modpaths:
                try:
                    name = get_mod_name(path)
                    name_list.append(name)
                except:
                    root.path.included_modpaths.pop()
                    msg.show_error(message=f"路徑{path}無法辨識為模組")
            info_strvar.set(f"當前引用模組:{name_list}")

        sel_mod_dir_btn = ttk.Button(master=root,
                                     text="引用模組",
                                     command=included_mod_dir_btn_command)
        sel_mod_dir_btn.pack(pady=20)

        def read_command():
            self.read_btn.config(state="disabled")
            root.has_updated = False

        self.read_btn = ttk.Button(master=root,
                                     text="開始讀取",
                                     style="danger",
                                     command=read_command)
        self.read_btn.pack(pady=20)

        info_strvar = ttk.StringVar(value="當前引用模組:")
        info_label = ttk.Label(master=root,
                               textvariable=info_strvar)
        info_label.pack(pady=20)
    
    def update_task(self) -> None:
        #檢查是否設定鋼四資料夾
        if not root.has_updated and root.path.hoi4path is not None:
            
            execute_list = list()
            args_list = list()
            callback_function_list = list()
            progress_msgs = list()

            def append_mission(mission,args,callback,msg):
                execute_list.append(mission)
                args_list.append(args)
                callback_function_list.append(callback)
                progress_msgs.append(msg)

            append_mission(check_path_avalibility,(),None,"確認路徑有效性")
            append_mission(integrate_path,(),None,"整合路徑")

            if not root.using_cache:
                append_mission(read_loc_files,(),None,"讀取本地化文件")
                append_mission(read_map_files,(),None,"讀取地圖")
                append_mission(read_country_tag_file,(),None,"讀取國家代碼")
                append_mission(read_country_color,(),None,"讀取國家配色")
                append_mission(create_province_map_image,(),None,"繪製省分地圖")
                append_mission(create_state_map_image,(),None,"繪製地塊地圖")
                append_mission(create_strategic_map_image,(),None,"繪製戰略區地圖")
                append_mission(create_nation_map_image,(),None,"繪製政權地圖")
            else:
                append_mission(load_cache,(),None,"讀取快取")

            if not root.using_cache:
                append_mission(save_cache,(),None,"建立快取")

            def update_btn(running_window): 
                '''
                確保在任務完成後才更新畫面
                '''
                self.character_btn.config(state="normal")
                self.map_view_btn.config(state="normal")
                self.read_btn.config(state="normal")
            append_mission(update_btn,(),None,"更新畫面")

            self.rw = RunningWindow(execute_list=execute_list,
                          args_list=args_list,
                          callback_function_list=callback_function_list,
                          prev=root,
                          title="執行中",
                          progress_msgs=progress_msgs)
            root.has_updated = True
        
        try:
            if self.rw.is_done: self.read_btn.config(state="normal")
        except Exception:
            pass
            
        root.after(ms=100,func=self.update_task)
    