'''
progress_window.py
用於呈現加載資料的視窗
'''

from typing import Callable
import queue
import threading

import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox as msg

class Progress_window:
    def __init__(self,
                 target:Callable,
                 args:tuple = (),
                 output_container = None,
                 prev: ttk.Toplevel | ttk.Window = None,
                 title:str = "提示",
                 progress_msg:str = "執行中") -> None:
        '''
        建立視窗並以`args`為參數執行`target`，輸出到`output_container`。
        :param target: 執行對象
        :param args: 執行參數
        :param output_container: 執行對象輸出位置
        :param prev: 引用的視窗
        :param title: 標題
        :param progress_msg: 執行時顯示的字串
        '''

        self.target = target
        self.args = args
        self.output_container = output_container
        self.prev = prev
        self.title = title
        self.progress_msg = progress_msg

        self.show_and_create_widget()

        #建立線程讀取本地化檔案
        self.is_cancel_task = False
        self.expection = None
        self.result_queue = queue.Queue()   #結果回傳佇列
        self.progress_queue = queue.Queue() #進度回傳佇列
        self.decorated_args = tuple([self]+list(self.args))
        thread = threading.Thread(target=self.target,
                                  daemon=True,
                                  args=self.decorated_args)
        thread.start()

        self.update_task()
    
    def show_and_create_widget(self) -> None:
        '''
        顯示並創建物件
        '''
        self.toplevel = ttk.Toplevel(title=self.progress_msg,
                                     size=(450,100),
                                     resizable=(False,False),
                                     transient=self.prev)
        self.toplevel.protocol("WM_DELETE_WINDOW",self.cancel_read_task)
        
        ttk.Label(master=self.toplevel,text=self.progress_msg).pack(side="left",padx=20)

        self.progress_bar = ttk.Progressbar(master=self.toplevel,
                                            length=200,
                                            mode='determinate')
        self.progress_bar.pack(side="left")

        self.cancel_btn = ttk.Button(master=self.toplevel,
                                     text="取消",
                                     style="secondary",
                                     command=self.cancel_read_task)
        self.cancel_btn.pack(side="left",padx=10)
    
    def update_task(self) -> None:
        '''
        更新畫面
        '''
        #用戶中斷
        if self.is_cancel_task:
            self.toplevel.destroy()
            msg.show_info(message="已中斷執行進度",
                          title=self.title,
                          parent=self.prev)
            return
        
        #更新進度值
        try:
            progress = self.progress_queue.get_nowait()
        except queue.Empty:
            progress = self.progress_bar["value"]
        
        #擷取錯誤
        if self.expection is not None:
            msg.show_warning(message=self.expection,title="錯誤!",parent=self.prev)
            return
        
        #嘗試獲取資料，如果沒有則更新進度條
        try:
            self.output_container = self.result_queue.get_nowait()
            self.toplevel.destroy()
            return 
        except queue.Empty:
            self.toplevel.after(ms=100,func=self.update_task)
            self.progress_bar["value"] = progress
    
    def cancel_read_task(self) -> None:
        '''
        取消讀取任務
        '''
        self.is_cancel_task = True