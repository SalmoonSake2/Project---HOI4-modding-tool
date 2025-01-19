'''
map_view.py
'''

from PIL import Image
import ttkbootstrap as ttk

from libs.interface.image_view import Imageview
from libs.map import Province, State
from libs.root import Root

class Mapview:
    '''
    地圖檢視器視窗
    '''

    def __init__(self,root:Root) -> None:
        self.root = root
        self.mode = "province"
        self.show_and_create_widget()
    
    def show_and_create_widget(self) -> None:
        
        toplevel = ttk.Toplevel(title="地圖檢視器",
                            size=(1050,600),
                            transient=self.root)
        
        map_frame = ttk.Frame(master=toplevel)
        map_frame.pack(side="left",fill="y")

        self.imageview = Imageview(master=map_frame,
                                   height=570,
                                   width=700,
                                   scale_restrction=(0.21,20),
                                   operation_key=("<MouseWheel>","<ButtonPress-2>","<B2-Motion>"),
                                   image=Image.open(self.root.hoi4path+"/map/provinces.bmp"))
        self.imageview.pack()

        self.imageview.create_rectangle(0,0,700,40,fill="#555555")
        self.imageview.create_text(10,10,text="省分ID:",fill="#CCCCCC",font="Helvetica 12",anchor="nw",tags="_text")
        self.imageview.create_text(560,10,text="座標:",fill="#CCCCCC",font="Helvetica 12",anchor="nw",tags="_coord")

        self.imageview.bind("<Motion>", self.get_hover_color)

        view_mode_frame = ttk.Frame(master=map_frame)
        view_mode_frame.pack(fill="x")

        view_mode = ("province","state","strategic","nation","river","heightmap","terrain")

        loc = ("省分","地塊","戰略區","政權","河流","高度圖","地形")
        view_mode_loc = dict(zip(view_mode,loc))

        btn_command = (self.province_mode,self.state_mode,None,self.nation_mode,self.river_mode,self.heightmap_mode,self.terrain_mode)
        view_mode_btn_command = dict(zip(view_mode,btn_command))

        view_mode_button = dict()

        for mode in view_mode:
            button = ttk.Button(master=view_mode_frame,
                                text=view_mode_loc[mode],
                                style="outline",
                                command=view_mode_btn_command[mode])
            view_mode_button[mode] = button
            view_mode_button[mode].pack(side="left")

        #檢視strategic region
        #繪製鐵路、補給基地
    
    def get_hover_color(self,event) -> None:
        '''
        獲取當前滑鼠所指的顏色並顯示座標及資訊
        '''
        if not self.imageview.image: return

        #將畫布座標轉為圖像座標
        canvas_x, canvas_y = self.imageview.canvasx(event.x), self.imageview.canvasy(event.y)
        img_x = int((canvas_x - self.imageview.offset_x) / self.imageview.image_scale_factor)
        img_y = int((canvas_y - self.imageview.offset_y) / self.imageview.image_scale_factor)

        # 確保座標合法
        is_valid_position = 0 <= img_x < self.imageview.image.width and 0 <= img_y < self.imageview.image.height

        if not is_valid_position: return
        
        if self.mode == "province":

            #獲取當前所指顏色
            color = self.imageview.image.getpixel((img_x, img_y))

            #以顏色獲取省分資料
            province_data = Province.get_province_from_color(self.root,color)

            terrain = province_data.terrain
            state = State.get_state_from_province(self.root,province_data)

            try:
                province_name = f"({self.root.loc_data[f"VICTORY_POINTS_{province_data.id}"]})"
            except:
                province_name = ""
            
            try:
                state_name = self.root.loc_data[f"STATE_{state.id}"] + f"(#{state.id})的"
            
            except:
                state_name = ""

            self.imageview.itemconfig("_text",text=f"{state_name}{self.root.loc_data[terrain]}省分(#{province_data.id} {province_name})")

        elif self.mode == "heightmap":
            color = self.imageview.image.getpixel((img_x, img_y))
            self.imageview.itemconfig("_text",text=f"高度:{color-95}")
        
        elif self.mode == "state":
            #獲取當前所指顏色
            color = self.imageview.image.getpixel((img_x, img_y))

            #以顏色獲取資料
            province_data = Province.get_province_from_color(self.root,color)

            state = State.get_state_from_province(self.root,province_data)

            if state is None:
                self.imageview.itemconfig("_text",text="海洋")

            else:
                self.imageview.itemconfig("_text",text=f"{self.root.loc_data["STATE_"+str(state.id)]}(#{state.id})")

        elif self.mode == "river":
            #獲取當前所指顏色
            color = self.imageview.image.convert("RGB").getpixel((img_x, img_y))

            river_color_mapping = {
                (0,255,0):"源頭",
                (255,0,0):"流入",
                (255,252,0):"分流",
                (0,255,255):"窄河流(超窄材質)",
                (0,200,255):"窄河流",
                (0,150,255):"窄河流",
                (0,100,255):"窄河流(寬材質)",
                (0,0,255):"寬河流",
                (0,0,225):"寬河流",
                (0,0,200):"寬河流",
                (0,0,150):"寬河流",
                (0,0,100):"寬河流(超寬材質)"
            }

            try:
                self.imageview.itemconfig("_text",text=river_color_mapping[color])
            
            except:
                self.imageview.itemconfig("_text",text="")

        elif self.mode == "terrain":
            #獲取當前所指顏色
            color = self.imageview.image.convert("RGB").getpixel((img_x, img_y))

            color_mapping = {
                (86,124,27):"平原",
                (0,86,6):"茂密的森林",
                (112,74,31):"丘陵",
                (206,169,99):"礫質沙漠",
                (6,200,11):"稀疏的森林",
                (255,0,24):"農田",
                (134,84,30):"山峰",
                (252,255,0):"砂質沙漠",
                (73,59,15):"岩質沙漠",
                (75,147,174):"沼澤地",
                (174,0,255):"熱帶山",
                (92,83,76):"溫帶山",
                (255,0,240):"沙漠邊緣",
                (240,255,0):"城市",
                (8,31,130):"海洋",
                (255,255,255):"被雪覆蓋的山",
                (132,255,0):"丘陵",
                (114,137,105):"被雪覆蓋的平原",
                (58,131,82):"山",
                (255,0,127):"叢林",
                (243,199,147):"山"
            }

            try:
                self.imageview.itemconfig("_text",text=color_mapping[color])
            
            except:
                self.imageview.itemconfig("_text",text="")

        elif self.mode == "nation":
            #獲取當前所指顏色
            color = self.root.state_map.getpixel((img_x, img_y))

            #以顏色獲取國家TAG
            try:
                country_tag = self.root.state_country_color_mapping[color]

                self.imageview.itemconfig("_text",text=f"{self.root.loc_data[country_tag+"_ADJ"]}({country_tag})")
            except:
                self.imageview.itemconfig("_text",text="")

        self.imageview.itemconfig("_coord",text=f"座標:({img_x},{img_y})")
                
    def river_mode(self) -> None:
        self.mode = "river"
        self.imageview.set_image(Image.open(self.root.hoi4path+"/map/rivers.bmp"))
    
    def province_mode(self) -> None:
        self.mode = "province"
        self.imageview.set_image(Image.open(self.root.hoi4path+"/map/provinces.bmp"))
    
    def heightmap_mode(self) -> None:
        self.mode = "heightmap"
        self.imageview.set_image(Image.open(self.root.hoi4path+"/map/heightmap.bmp"))
    
    def terrain_mode(self) -> None:
        self.mode = "terrain"
        self.imageview.set_image(Image.open(self.root.hoi4path+"/map/terrain.bmp"))

    def state_mode(self) -> None:
        self.mode = "state"
        self.imageview.set_image(self.root.state_map)

    def nation_mode(self) -> None:
        self.mode = "nation"
        self.imageview.set_image(self.root.nation_map)