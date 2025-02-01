'''
map_view.py
'''

from typing import Literal

import ttkbootstrap as ttk

from libs.enums import *
from libs.interface.localisation import loc
from libs.interface.image_view import Imageview
from libs.map import *
from libs.stringutil import listring
from libs.root import root

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
        
        self.info_frame = ttk.Labelframe(master=toplevel,width=350,text="詳細資訊")
        self.info_frame.pack(side="left",fill="both",expand=True,padx=5,pady=5)
        self.inner_info_frame = ttk.Frame(master=self.info_frame)
        self.inner_info_frame.pack(fill="both")
    
    def show_map_item(self,event) -> None:
        '''
        顯示選中物件的資訊
        '''
        img_position = self.imageview.get_image_postion(event.x,event.y)

        if img_position is not None:
            img_x, img_y = img_position
        
        else:
            return
        
        self.inner_info_frame.destroy()
        self.inner_info_frame = ttk.Frame(master=self.info_frame)
        self.inner_info_frame.pack(side="left",fill="both",pady=10)

        if self.mode == "province":
            color = root.game_image.province_image.getpixel((img_x, img_y))
            province_data = Province.from_color(color)
            name_label = ttk.Label(master=self.inner_info_frame,text="名稱: "+loc(f"VICTORY_POINTS_{province_data.id}"))
            name_label.grid(column=0,row=0,padx=10,sticky=ttk.W)
            id_label = ttk.Label(master=self.inner_info_frame,text="ID: "+str(province_data.id))
            id_label.grid(column=0,row=1,padx=10,sticky=ttk.W)
            terrain_label = ttk.Label(master=self.inner_info_frame,text="地形: "+loc(province_data.terrain))
            terrain_label.grid(column=0,row=2,padx=10,sticky=ttk.W)
            continent_label = ttk.Label(master=self.inner_info_frame,text="大陸: "+loc(root.map_data.continents[province_data.continent]) if province_data.continent != 0 else "大陸: 無歸屬")
            continent_label.grid(column=0,row=3,padx=10,sticky=ttk.W)

            if province_data.type == "sea":
                province_type = "海洋"
            
            elif province_data.type == "land" and province_data.coastal == True:
                province_type = "海岸"
            
            else:
                province_type = "陸地"

            type_label = ttk.Label(master=self.inner_info_frame,text="類型: "+province_type)
            type_label.grid(column=0,row=4,padx=10,sticky=ttk.W)
        
        elif self.mode == "state":
            color = root.game_image.state_map.getpixel((img_x, img_y))
            try:
                state_data = State.from_province_id(Province.from_color(color).id)
            except:
                return
            name_label = ttk.Label(master=self.inner_info_frame,text="名稱: "+loc(f"STATE_{state_data.id}"))
            name_label.grid(row=0,column=0,padx=10,sticky=ttk.W)
            id_label = ttk.Label(master=self.inner_info_frame,text="ID: "+str(state_data.id))
            id_label.grid(row=1,column=0,padx=10,sticky=ttk.W)
            manpower_label = ttk.Label(master=self.inner_info_frame,text="人口: "+str(state_data.manpower))
            manpower_label.grid(row=2,column=0,padx=10,sticky=ttk.W)
            category_label = ttk.Label(master=self.inner_info_frame,text="類型: "+loc(state_data.state_category))
            category_label.grid(row=3,column=0,padx=10,sticky=ttk.W)
            owner_label = ttk.Label(master=self.inner_info_frame,text="擁有者: "+loc(state_data.owner)+"("+str(state_data.owner)+")")
            owner_label.grid(row=4,column=0,padx=10,sticky=ttk.W)
            local_supply_label = ttk.Label(master=self.inner_info_frame,text="當地補給: "+str(state_data.local_supply))
            local_supply_label.grid(row=5,column=0,padx=10,sticky=ttk.W)

            if state_data.core is not None:

                core_text = ""

                if isinstance(state_data.core,list):
                    for nation in state_data.core:
                        core_text += loc(nation)+"("+str(nation)+") "
                
                else:
                    core_text += loc(state_data.core)+"("+str(state_data.core)+") "
            
            else: 
                core_text = "無"
                
            core_label = ttk.Label(master=self.inner_info_frame,text=f"核心: {core_text}")
            core_label.grid(row=6,column=0,padx=10,sticky=ttk.W)

            if state_data.claim is not None:

                claim_text = ""

                if isinstance(state_data.claim,list):
                    for nation in state_data.claim:
                        claim_text += loc(nation)+"("+str(nation)+") "
                
                else:
                    claim_text += loc(state_data.claim)+"("+str(state_data.claim)+") "
            
            else: 
                claim_text = "無"
                
            claim_label = ttk.Label(master=self.inner_info_frame,text=f"宣稱: {claim_text}")
            claim_label.grid(row=7,column=0,padx=10,sticky=ttk.W)

            resource_text = ""

            if state_data.resources is not None:
                for resource in state_data.resources:
                    resource_text += loc(f"PRODUCTION_MATERIALS_{resource.upper()}")+f"x{int(state_data.resources[resource])} "

            else:
                resource_text = "無"

            resource_label = ttk.Label(master=self.inner_info_frame,text=f"資源: {resource_text}")
            resource_label.grid(row=8,column=0,padx=10,sticky=ttk.W)

            building_text = ""

            if state_data.buildings is not None:
                for building in state_data.buildings:
                    building_text += loc(building.name)+f"x{building.level} "

            else:
                building_text = "無"

            building_label = ttk.Label(master=self.inner_info_frame,text=f"建築: {building_text}")
            building_label.grid(row=9,column=0,padx=10,sticky=ttk.W)

            if state_data.demilitarized_zone or state_data.impassable:

                special_property_text = ""

                if state_data.demilitarized_zone:
                    special_property_text += "非軍事區 "
                
                if state_data.impassable:
                    special_property_text += "不可通行 "

                special_property_label = ttk.Label(master=self.inner_info_frame,text=special_property_text,style=ttk.DANGER)
                special_property_label.grid(row=100,column=0,padx=10,sticky=ttk.W)

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
            state = State.from_province_id(province_data.id)

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

            if province_data is not None:
                state = State.from_province_id(province_data.id)

            if province_data is None:
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
                country_tag = State.from_province_id(Province.from_color(color).id).owner

                self.imageview.itemconfig("_text",text=f"{loc(country_tag+"_DEF")}({country_tag})")
            except:
                self.imageview.itemconfig("_text",text="")

        elif self.mode == "strategic":
            try:
                strategic = StrategicRegion.from_province_id(Province.from_color(color).id)

                self.imageview.itemconfig("_text",text=f"{loc(root.map_data.strategicregions[strategic.id].name)}(#{strategic.id})")
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
        
        self.inner_info_frame.destroy()
        self.inner_info_frame = ttk.Frame(master=self.info_frame)
        self.inner_info_frame.pack()
            
        self.imageview.set_image(using_image)