'''
map_view.py
'''

from typing import Literal

import ttkbootstrap as ttk

from libs.enums import *
from libs.interface.image_view import Imageview
from libs.map import Province, State
from libs.root import root,loc

class Mapview:
    '''
    地圖檢視器視窗
    '''

    def __init__(self,prev:ttk.Toplevel | ttk.Window) -> None:
        self.prev = prev
        self.show_and_create_widget()
        self.mode = "province"
    
    def show_and_create_widget(self) -> None:
        
        toplevel = ttk.Toplevel(title="地圖檢視器",
                            size=(1300,900),
                            transient=self.prev)
        
        map_frame = ttk.Frame(master=toplevel)
        map_frame.pack(side="left",fill="y")

        self.imageview = Imageview(master=map_frame,
                                   height=40,
                                   width=900,
                                   scale_restrction=(0.21,20),
                                   operation_key=("<MouseWheel>","<ButtonPress-2>","<B2-Motion>"),
                                   image=root.game_image.province_map)
        self.imageview.pack(fill="y",expand=True)

        self.imageview.create_rectangle(0,0,900,40,fill="#555555")
        self.imageview.create_text(10,10,text="省分ID:",fill="#CCCCCC",font="Helvetica 12",anchor="nw",tags="_text")
        self.imageview.create_text(760,10,text="座標:",fill="#CCCCCC",font="Helvetica 12",anchor="nw",tags="_coord")

        self.imageview.bind("<Motion>", self.get_hover_color)
        self.imageview.bind("<ButtonPress-1>",self.show_map_item)

        view_mode_frame = ttk.Frame(master=map_frame)
        view_mode_frame.pack(fill="x")

        view_mode = ("province","state","strategic","nation","river","heightmap","terrain")
        view_mode_loc = dict(zip(view_mode,("省分","地塊","戰略區","政權","河流","高度圖","地形")))

        view_mode_button:dict[str,ttk.Button] = dict()

        for mode in view_mode:
            button = ttk.Button(master=view_mode_frame,
                                text=view_mode_loc[mode],
                                style="outline",
                                command=lambda x=mode:self.set_view_mode(x))
            view_mode_button[mode] = button
            view_mode_button[mode].pack(side="left",pady=5)
        
        info_frame = ttk.Labelframe(master=toplevel,width=350,text="詳細資訊")
        info_frame.pack(side="left",fill="both",expand=True,padx=5,pady=5)
    
    def show_map_item(self,event) -> None:
        '''
        顯示選中物件的資訊
        '''
        ...

    def get_hover_color(self,event) -> None:
        '''
        獲取當前滑鼠所指的顏色並顯示座標及資訊
        '''
        img_position = self.imageview.get_image_postion(event.x,event.y)

        if img_position is not None:
            img_x, img_y = img_position
        
        else:
            return

        color = self.imageview.image.convert("RGB").getpixel((img_x, img_y))
        
        if self.mode == "province":

            #使用province.bmp分析，而非當前圖像
            color = root.game_image.province_image.getpixel((img_x, img_y))

            province_data = Province.from_color(color)

            terrain = province_data.terrain
            state = State.from_province(province_data)

            province_name = f"({loc(f"VICTORY_POINTS_{province_data.id}")})"
            
            if "VICTORY_POINTS_" in province_name: province_name = ""

            if state is not None:
                state_name = loc(f"STATE_{state.id}") + f"(#{state.id})的"
            else:
                state_name = ""

            self.imageview.itemconfig("_text",text=f"{state_name}{loc(terrain)}省分(#{province_data.id} {province_name})")

        elif self.mode == "heightmap":
            #灰階圖像
            color = self.imageview.image.getpixel((img_x, img_y))
            self.imageview.itemconfig("_text",text=f"高度:{color}")
        
        elif self.mode == "state":
            #以顏色獲取資料
            province_data = Province.from_color(color)

            state = State.from_province(province_data)

            if state is None:
                self.imageview.itemconfig("_text",text="海洋")

            else:
                self.imageview.itemconfig("_text",text=f"{loc("STATE_"+str(state.id))}(#{state.id})")

        elif self.mode == "river":
            try:
                self.imageview.itemconfig("_text",text=RIVERCOLOR[color])
            
            except:
                self.imageview.itemconfig("_text",text="")

        elif self.mode == "terrain":
            try:
                self.imageview.itemconfig("_text",text=TERRAINCOLOR[color])
            
            except:
                self.imageview.itemconfig("_text",text="")

        elif self.mode == "nation":
            #以state視圖分析
            color = root.game_image.state_map.getpixel((img_x, img_y))

            #以顏色獲取國家TAG
            try:
                country_tag = root.state_country_color_mapping[color]

                self.imageview.itemconfig("_text",text=f"{loc(country_tag+"_DEF")}({country_tag})")
            except:
                self.imageview.itemconfig("_text",text="")

        elif self.mode == "strategic":
            try:
                strategic_id = root.province_strategic_mapping[Province.from_color(color).id]

                self.imageview.itemconfig("_text",text=f"{loc(root.map_data["strategicregion"][strategic_id][0]["name"].strip('"'))}(#{strategic_id})")
            except:
                self.imageview.itemconfig("_text",text="")

        self.imageview.itemconfig("_coord",text=f"座標:({img_x},{img_y})")

    def set_view_mode(self,mode_name:Literal["province","state","strategic","nation","river","heightmap","terrain"]) -> None:
        '''
        設定視圖模式
        '''
        self.mode = mode_name

        match self.mode:
            case "province":    using_image = root.game_image.province_map
            case "state":       using_image = root.game_image.state_map
            case "strategic":   using_image = root.game_image.strategic_map
            case "nation":      using_image = root.game_image.nation_map
            case "river":       using_image = root.game_image.rivers_image
            case "heightmap":   using_image = root.game_image.heightmap_image
            case "terrain":     using_image = root.game_image.terrain_image
            
        self.imageview.set_image(using_image)