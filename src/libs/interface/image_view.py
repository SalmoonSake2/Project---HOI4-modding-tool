'''
image_view.py
圖片檢視器元件
'''
from PIL import Image, ImageTk
import ttkbootstrap as ttk

class Imageview(ttk.Canvas):

    def __init__(self, 
                 image:Image.Image | None = None,
                 scale_restrction: tuple = (0.1, 10), 
                 always_bg:bool = True,
                 **kwargs):
        '''
        Construct a imageview widget with the parent master.

        Valid resource names: background, bd, bg, borderwidth, closeenough,
        confine, cursor, height, highlightbackground, highlightcolor,
        highlightthickness, image, insertbackground, insertborderwidth,
        insertofftime, insertontime, insertwidth, offset, relief, scale_restrction,
        scrollregion, selectbackground, selectborderwidth, selectforeground,
        state, takefocus, width, xscrollcommand, xscrollincrement,
        yscrollcommand, yscrollincrement.
        '''

        super().__init__(**kwargs)
        self.image = image
        self.image_tk = ImageTk.PhotoImage(self.image)

        self.image_scale_factor = 1.0
        self.min_scale, self.max_scale = scale_restrction

        #當前窗口在圖像上的偏移座標
        self.offset_x, self.offset_y = (0, 0)

        self.always_bg = always_bg

        self.create_image(0, 0, image=self.image_tk, anchor=ttk.NW,tag="_image")

        if self.always_bg:
            self.tag_lower("_image")

        # 配置互動(滾輪縮放、拖曳)
        self.bind("<MouseWheel>", self._zoom)
        self.bind("<ButtonPress-1>", self._start_pan)
        self.bind("<B1-Motion>", self._pan)

    def _zoom(self, event):

        last_scale_factor = self.image_scale_factor

        #如果當前倍率正常則放大
        if event.delta > 0 and self.image_scale_factor * 1.1 < self.max_scale:
            self.image_scale_factor *= 1.1
        
        #如果當前倍率正常則縮小
        elif event.delta < 0 and self.image_scale_factor * 0.9 > self.min_scale:
            self.image_scale_factor *= 0.9

        #根據鼠標位置縮放時進行偏移
        mouse_x, mouse_y = self.canvasx(event.x), self.canvasy(event.y)

        self.offset_x += (mouse_x - self.offset_x) * (1 - self.image_scale_factor / last_scale_factor)
        self.offset_y += (mouse_y - self.offset_y) * (1 - self.image_scale_factor / last_scale_factor)

        if self.image:
            self._render_task()

    def _start_pan(self, event):
        #獲取使用者開始拖曳的"元件"座標
        self.drag_mark_x, self.drag_mark_y = event.x, event.y

    def _pan(self, event):

        if self.image is None: return 

        #獲取鼠標偏移數據並更新當前偏移值(注意:鼠標向(+)移動時圖片讀取框會向(-)移動)
        delta_x = event.x - self.drag_mark_x
        delta_y = event.y - self.drag_mark_y
        
        #更新偏移座標
        self.offset_x += delta_x
        self.offset_y += delta_y
        self.drag_mark_x, self.drag_mark_y = (event.x, event.y)

        self._render_task()

    def _render_task(self) -> None:

        w, h = self.image.size
        canvas_width, canvas_height = (self.winfo_width(), self.winfo_height())

        # 顯示窗口在"圖片"的座標
        view_x0 = max(0, int(-self.offset_x / self.image_scale_factor))
        view_y0 = max(0, int(-self.offset_y / self.image_scale_factor))
        view_x1 = min(w, int((canvas_width - self.offset_x) / self.image_scale_factor))
        view_y1 = min(h, int((canvas_height - self.offset_y) / self.image_scale_factor))

        #座標正常才刷新
        if view_x1 > view_x0 and view_y1 > view_y0:

            # 只保留圖片可見區域
            cropped_img = self.image.crop((view_x0, view_y0, view_x1, view_y1))
            cropped_w = view_x1 - view_x0
            cropped_h = view_y1 - view_y0

            # 縮放
            if int(cropped_w * self.image_scale_factor) > 0 and int(cropped_h * self.image_scale_factor) > 0:
                scaled_cropped_img = cropped_img.resize(
                    size=(int(cropped_w * self.image_scale_factor), int(cropped_h * self.image_scale_factor)),
                    resample=Image.Resampling.NEAREST,
                )
            
            else:
                scaled_cropped_img = cropped_img

            # 更新顯示圖像
            self.image_tk = ImageTk.PhotoImage(scaled_cropped_img)
            self.delete("_image")
            self.create_image(
                self.offset_x + view_x0 * self.image_scale_factor,
                self.offset_y + view_y0 * self.image_scale_factor,
                image=self.image_tk,
                anchor=ttk.NW,
                tag="_image"
            )

            if self.always_bg:
                self.tag_lower("_image")