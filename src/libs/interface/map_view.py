'''
map_view.py
'''

from PIL import Image
import ttkbootstrap as ttk

from libs.interface.image_view import Imageview
from libs.interface_io.get_province_from_color import get_province_from_color
from libs.root import Root

class Mapview:

    def __init__(self,root:Root) -> None:
        self.root = root
        self.show_and_create_widget()
    
    def show_and_create_widget(self) -> None:
        
        toplevel = ttk.Toplevel(title="地圖檢視器",
                            size=(750,570),
                            transient=self.root)
        
        self.imageview = Imageview(master=toplevel,
                              height=570,
                              width=700,
                              scale_restrction=(0.21,20),
                              image=Image.open(self.root.hoi4path+"/map/provinces.bmp"))
        self.imageview.pack(side="left")

        self.imageview.create_rectangle(0,0,400,40,fill="#555555")
        self.imageview.create_text(10,10,text="省分ID:",fill="#CCCCCC",font="Helvetica 18",anchor="nw",tags="_text")

        self.imageview.bind("<Motion>", self.get_hover_color)

        #檢視province, state, strategic region
        #繪製省分、河流、高度圖、地形外觀、樹種、設定資料
        #導入n貼圖、unitstack、buildings
        #繪製鐵路、補給基地
    
    def get_hover_color(self,event) -> None:
        '''
        獲取當前滑鼠所指的顏色
        '''
        if self.imageview.image:
            # 将 Canvas 坐标转换为图像坐标
            canvas_x, canvas_y = self.imageview.canvasx(event.x), self.imageview.canvasy(event.y)
            img_x = int((canvas_x - self.imageview.offset_x) / self.imageview.image_scale_factor)
            img_y = int((canvas_y - self.imageview.offset_y) / self.imageview.image_scale_factor)

            # 确保坐标在图像范围内
            if 0 <= img_x < self.imageview.image.width and 0 <= img_y < self.imageview.image.height:
                color = self.imageview.image.getpixel((img_x, img_y))  # 获取像素颜色

                province_id = get_province_from_color(self.root,color)

                province_data = self.root.map_data["province"][self.root.map_data["province"]["id"] == province_id][0]
                terrain = province_data["category"]
                try:
                    province_name = f"({self.root.loc_data[f"VICTORY_POINTS_{province_id}"]})"
                except:
                    province_name = ""

                self.imageview.itemconfig("_text",text=f"{self.root.loc_data[terrain]}省分ID:{province_id} {province_name}")
                

        
