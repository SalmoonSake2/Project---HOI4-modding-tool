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
                            size=(750,570),
                            transient=self.root)
        
        self.imageview = Imageview(master=toplevel,
                                   height=570,
                                   width=700,
                                   scale_restrction=(0.21,20),
                                   operation_key=("<MouseWheel>","<ButtonPress-2>","<B2-Motion>"),
                                   image=Image.open(self.root.hoi4path+"/map/provinces.bmp"))
        self.imageview.pack(side="left")

        self.imageview.create_rectangle(0,0,700,40,fill="#555555")
        self.imageview.create_text(10,10,text="省分ID:",fill="#CCCCCC",font="Helvetica 12",anchor="nw",tags="_text")
        self.imageview.create_text(560,10,text="座標:",fill="#CCCCCC",font="Helvetica 12",anchor="nw",tags="_coord")

        self.imageview.bind("<Motion>", self.get_hover_color)
        toplevel.bind("<KeyPress-r>",self.river_mode)
        toplevel.bind("<KeyPress-p>",self.province_mode)
        toplevel.bind("<KeyPress-h>",self.heightmap_mode)
        toplevel.bind("<KeyPress-t>",self.terrain_mode)
        toplevel.bind("<KeyPress-s>",self.state_mode)

        #檢視province, state, strategic region
        #繪製鐵路、補給基地
    
    def get_hover_color(self,event) -> None:
        '''
        獲取當前滑鼠所指的顏色並顯示座標
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

        self.imageview.itemconfig("_coord",text=f"座標:({img_x},{img_y})")
                

    def river_mode(self,event) -> None:
        self.mode = "river"
        self.imageview.set_image(Image.open(self.root.hoi4path+"/map/rivers.bmp"))
    
    def province_mode(self,event) -> None:
        self.mode = "province"
        self.imageview.set_image(Image.open(self.root.hoi4path+"/map/provinces.bmp"))
    
    def heightmap_mode(self,event) -> None:
        self.mode = "heightmap"
        self.imageview.set_image(Image.open(self.root.hoi4path+"/map/heightmap.bmp"))
    
    def terrain_mode(self,event) -> None:
        self.mode = "terrain"
        self.imageview.set_image(Image.open(self.root.hoi4path+"/map/terrain.bmp"))

    def state_mode(self,event) -> None:
        self.mode = "state"
        self.imageview.set_image(self.root.state_map)
