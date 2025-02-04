'''
hoi4_modding_tool.py

程式的本體
'''

from tkinter import filedialog

from PIL import Image,ImageTk
from pathlib import Path
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox as msg
from ttkbootstrap.tooltip import ToolTip

from libs.interface.character_creater import Character_creater
from libs.interface.map_view import Mapview
from libs.interface.running_window import RunningWindow
from libs.reader.cache_reader import save_cache, load_cache
from libs.reader.reader import *
from libs.root import root

class App:
    def __init__(self) -> None:

        self.has_cache = False

        self.show_and_create_widget()
        self.find_hoi4_path()
        self.update_task()
        root.mainloop()
    
    def find_hoi4_path(self) -> None:
        common_game_path = "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV"
        root.path.hoi4path = common_game_path if Path(common_game_path).exists() else None
        self.hoi4pathvar.set("遊戲路徑:"+root.path.hoi4path)

    def create_menu_bar(self) -> None:
        '''
        建立目錄列
        '''
        menubar = ttk.Menu(master=root)
        root.config(menu=menubar)

        ###########################################################################################

        def select_mod_path():
            resp = filedialog.askdirectory()
            if resp: 
                root.path.modpath = resp
        
        def select_game_path():
            resp = filedialog.askdirectory()
            if resp: 
                root.path.hoi4path = resp
                self.hoi4pathvar.set("遊戲路徑:"+root.path.hoi4path)
        
        def select_import_mod_path():
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

        file_menu = ttk.Menu(master=menubar)
        file_menu.add_command(label="選擇模組資料夾",command=select_mod_path)
        file_menu.add_command(label="選擇遊戲資料夾",command=select_game_path)
        file_menu.add_command(label="引用模組",command=select_import_mod_path)
        file_menu.add_separator()

        self.load_data_menu = ttk.Menu(master=file_menu)

        def read_and_load_command(is_using_cache:bool):
            self.load_data_menu.entryconfig("使用快取匯入",state="disabled")
            self.load_data_menu.entryconfig("建立快取並匯入",state="disabled")
            self.read_and_load_file(is_using_cache)

        self.load_data_menu.add_command(label="使用快取匯入",command= lambda x = True:read_and_load_command(x),state=ttk.DISABLED)
        self.load_data_menu.add_command(label="建立快取並匯入",command= lambda x = False:read_and_load_command(x))

        file_menu.add_cascade(label="匯入資料",menu=self.load_data_menu)
        file_menu.add_command(label="輸出",state=ttk.DISABLED)
        menubar.add_cascade(menu=file_menu,label="檔案")

        ###########################################################################################

        option_menu = ttk.Menu(master=menubar)
        menubar.add_cascade(menu=option_menu,label="設定")

        ###########################################################################################

        info_menu = ttk.Menu(master=menubar)
        info_menu.add_command(label="操作手冊")
        info_menu.add_command(label="關於")
        menubar.add_cascade(menu=info_menu,label="說明")

    def show_and_create_widget(self) -> None:
        '''
        建立畫面的物件
        '''
        self.create_menu_bar()

        bottom_bar = ttk.Frame(master=root,height=20,style=ttk.DARK)
        bottom_bar.pack(side="bottom",fill="x")

        self.hoi4pathvar = ttk.StringVar(master=root,value="未指派遊戲路徑")
        hoi4path_label = ttk.Label(master=bottom_bar,textvariable=self.hoi4pathvar,style=(ttk.INVERSE,ttk.DARK))
        hoi4path_label.pack(side="right",padx=10)

        sidebar = ttk.Frame(master=root,width=50)
        sidebar.pack(side="left",fill="y")

        side_sep = ttk.Separator(master=root,orient="vertical",style=ttk.DARK)
        side_sep.pack(side="left",fill="y")

        sidebar_btns:dict[str,ttk.Button] = dict.fromkeys (("map_creater",
                                                           "focus_creater",
                                                            "character_creater",
                                                            "trait_creater",
                                                            "event_creater",
                                                            "decision_creater"))
        tooltip_text:dict[str,str] = {
            "map_creater":"地圖編輯器",
            "focus_creater":"國策編輯器",
            "character_creater":"角色編輯器",
            "trait_creater":"特質編輯器",
            "event_creater":"事件編輯器",
            "decision_creater":"決議/任務編輯器"
        }

        for sidebar_btn in sidebar_btns:
            sidebar_btns[sidebar_btn] = ttk.Button(master=sidebar,style=(ttk.LINK,ttk.DARK))
            sidebar_btns[sidebar_btn].image = ImageTk.PhotoImage(Image.open(f"assets/{sidebar_btn}.png"))
            sidebar_btns[sidebar_btn].config(image=sidebar_btns[sidebar_btn].image)
            sidebar_btns[sidebar_btn].pack()
            ToolTip(sidebar_btns[sidebar_btn],text=tooltip_text[sidebar_btn],bootstyle=ttk.LIGHT)

        def character_creater_command(x):#TODO 需要更好的檢查方式
            if len(root.map_data.province) != 0:
                Character_creater(x)
            else:
                msg.show_warning(message="尚未匯入資料",title="提示")
        
        def mapview_command(x):#TODO 需要更好的檢查方式
            if len(root.map_data.province) != 0:
                Mapview(x)
            else:
                msg.show_warning(message="尚未匯入資料",title="提示")
        
        sidebar_btns["map_creater"].config(command=lambda x=root:mapview_command(x))
        sidebar_btns["character_creater"].config(command=lambda x=root:character_creater_command(x))
    
    def read_and_load_file(self,is_using_cache:bool) -> None:
        '''
        讀取遊戲資料，不論用快取或直接讀取
        '''
        root.using_cache = is_using_cache
        
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
            append_mission(read_buildings_files,(),None,"讀取建築")
            append_mission(save_cache,(),None,"建立快取")
        else:
            append_mission(load_cache,(),None,"讀取快取")

        def update_btn(running_window): 
            self.load_data_menu.entryconfig("使用快取匯入",state="normal")
            self.load_data_menu.entryconfig("建立快取並匯入",state="normal")

        append_mission(update_btn,(),None,"更新畫面")

        RunningWindow(execute_list=execute_list,
                      args_list=args_list,
                      callback_function_list=callback_function_list,
                      prev=root,
                      title="執行中",
                      progress_msgs=progress_msgs)

    def update_task(self) -> None:
        '''
        隨時的更新
        '''

        if Path("data/cache.dat").exists() and not self.has_cache:
            self.load_data_menu.entryconfig("使用快取匯入",state=ttk.NORMAL)
            self.has_cache = True
        
        elif not Path("data/cache.dat").exists() and self.has_cache:
            self.load_data_menu.entryconfig("使用快取匯入",state=ttk.DISABLED)
            self.has_cache = False

        root.after(ms=500,func=self.update_task)
    