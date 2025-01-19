'''
image_view.py
圖片檢視器元件
'''
from PIL import Image, ImageTk
import ttkbootstrap as ttk

class Imageview(ttk.Canvas):
    '''
    圖片檢視器元件
    '''
    def __init__(self, 
                 image:Image.Image | None = None,
                 scale_restrction: tuple = (0.1, 10), 
                 always_bg:bool = True,
                 operation_key:tuple[str] = ("<MouseWheel>","<ButtonPress-1>","<B1-Motion>"),
                 **kwargs):
        '''
        圖片檢視元件，繼承自ttkbootstrap.Canvas。

        :param image: 欲顯示的圖片
        :param scale_restrction: 最小與最大縮放限制
        :param always_bg: 圖片是否總是在最下層
        :param operation_key: 操作的按鍵(縮放,開始拖曳,拖曳)
        '''

        super().__init__(**kwargs)
        self.image = image
        self.image_tk = ImageTk.PhotoImage(self.image)

        self.image_scale_factor = 1.0
        self.min_scale, self.max_scale = scale_restrction

        #當前窗口在圖像上的偏移座標
        self.offset_x, self.offset_y = (0, 0)

        self.always_bg = always_bg

        self.create_image(0, 0, image=self.image_tk, anchor=ttk.NW,tag="_image_28a391cf82739")#單純沒有意義的hash，避免衝突

        if self.always_bg:
            self.tag_lower("_image_28a391cf82739")

        # 配置互動(滾輪縮放、拖曳)
        self.bind(operation_key[0], self._zoom)
        self.bind(operation_key[1], self._start_pan)
        self.bind(operation_key[2], self._pan)

    def _zoom(self, event):
        '''
        內部方法，用於處理縮放時的操作
        '''
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
        '''
        內部方法，用於開始拖曳時的操作。獲取使用者開始拖曳的座標以平滑地拖曳。
        '''
        self.drag_mark_x, self.drag_mark_y = event.x, event.y

    def _pan(self, event):
        '''
        內部方法，用於處理拖曳時的操作
        '''
        if self.image is None: return 

        #獲取當前座標與開始時的偏移
        delta_x = event.x - self.drag_mark_x
        delta_y = event.y - self.drag_mark_y
        
        #更新偏移座標
        self.offset_x += delta_x
        self.offset_y += delta_y
        self.drag_mark_x, self.drag_mark_y = (event.x, event.y)

        self._render_task()

    def _render_task(self) -> None:
        '''
        內部方法，重新渲染畫面。
        '''
        w, h = self.image.size
        canvas_width, canvas_height = (self.winfo_width(), self.winfo_height())

        # 顯示窗口在"圖片"的座標
        view_x0 = max(0, int(-self.offset_x / self.image_scale_factor))
        view_y0 = max(0, int(-self.offset_y / self.image_scale_factor))
        view_x1 = min(w, int((canvas_width - self.offset_x) / self.image_scale_factor))
        view_y1 = min(h, int((canvas_height - self.offset_y) / self.image_scale_factor))

        #座標正常才刷新
        if not (view_x1 > view_x0 and view_y1 > view_y0): return
            
        #只保留圖片可見區域並裁切
        cropped_img = self.image.crop((view_x0, view_y0, view_x1, view_y1))

        #裁切後的圖片大小
        cropped_w = view_x1 - view_x0
        cropped_h = view_y1 - view_y0

        #縮放裁切影像至視窗大小
        if int(cropped_w * self.image_scale_factor) > 0 and int(cropped_h * self.image_scale_factor) > 0:
            scaled_cropped_img = cropped_img.resize(
                size=(int(cropped_w * self.image_scale_factor), int(cropped_h * self.image_scale_factor)),
                resample=Image.Resampling.NEAREST,
            )
        
        else:
            scaled_cropped_img = cropped_img

        # 更新顯示圖像
        self.image_tk = ImageTk.PhotoImage(scaled_cropped_img)
        self.delete("_image_28a391cf82739")
        self.create_image(
            self.offset_x + view_x0 * self.image_scale_factor,
            self.offset_y + view_y0 * self.image_scale_factor,
            image=self.image_tk,
            anchor=ttk.NW,
            tag="_image_28a391cf82739"
        )

        if self.always_bg:
            self.tag_lower("_image_28a391cf82739")