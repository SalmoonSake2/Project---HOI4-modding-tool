'''
progress_window.py
用於呈現加載資料的視窗
'''

import time
from typing import Callable
import queue
import threading

import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox as msg

class Progress_window:
    def __init__(self,
                 target:Callable,
                 args:tuple = (),
                 callback_function:Callable = None,
                 wait_until:Callable = lambda:True,
                 prev: ttk.Toplevel | ttk.Window = None,
                 title:str = "提示",
                 progress_msg:str = "執行中") -> None:
        '''
        建立視窗並以`args`為參數執行`target`，如果指定了wait_until，則wait_until為True時才會開始執行。
        :param target: 執行對象
        :param args: 執行參數
        :param callback_function: 回傳函數
        :param wait_until: 等待該判斷式為True時便會執行
        :param prev: 引用的視窗
        :param title: 標題
        :param progress_msg: 執行時顯示的字串
        '''

        self.target = target
        self.args = args
        self.callback_function = callback_function
        self.wait_until = wait_until
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

        def waiting_to_run(expression:Callable,function:Callable,args:tuple) -> None:
            while not expression():
                time.sleep(0.1) #檢查太快會導致CPU當機
            function(*args)

        waiting_thread = threading.Thread(target=waiting_to_run,daemon=True,args=(self.wait_until,
                                                                                  self.target,
                                                                                  self.decorated_args))

        waiting_thread.start()
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
            msg.show_warning(message=str(self.expection),title="錯誤!",parent=self.prev)
            self.toplevel.destroy()
            return
        
        #嘗試獲取資料，如果沒有則更新進度條
        try:
            self.callback_function(self.result_queue.get_nowait())

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