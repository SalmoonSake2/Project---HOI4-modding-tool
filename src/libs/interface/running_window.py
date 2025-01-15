'''
running_window.py

用於執行的物件，呼叫後會執行並生成視窗展示進度；支援序列式執行。
'''

from typing import Callable, Iterable
from threading import Thread

import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox as msg

class RunningWindow:
    
    def __init__(self,
                 execute_list: Callable | Iterable[Callable],
                 args_list: tuple | Iterable[tuple] | None = None,
                 callback_function_list: Callable | Iterable[Callable] | None = None,
                 prev: ttk.Window | ttk.Toplevel | None = None,
                 title: str = "My app",
                 progress_msgs: str | Iterable[str] = None) -> None:
        '''
        用於執行的物件，呼叫後會執行並生成視窗展示進度。\n
        代入的函數需要注意以下事項：\n
        - 需要有running_window參數，即便沒有使用\n
        - 遇到需要raise錯誤的地方則設定`running_window.exception`用於錯誤字串顯示。\n
        - 上述行為之後直接return就好，不用設定其他。\n
        - 需要在`running_window.is_cancel_task`為True時返回。\n
        - 定期向`running_window.progress_var`改變進度值，否則將不會有進度顯示。\n

        :param execute_list: 一個可執行項目或待執行清單，如果是清單，那麼將由第一個開始執行，直到完成輸出才會再執行下一個。\n
                             每個函數都需要在當中加入`running_window`參數。
        :param args_list: 一個參數元組或參數元組清單，用於代入`execute_list` 中的執行項目。
        :param callback_function_list: 返回函數或其列表，會在`execute_list`中的物件執行完成後被呼叫，參數是執行的return。\n
                                   如果執行物件有raise產生，則`callback_function` 不會被呼叫。
        :param prev: 引用本物件的視窗。
        :param title: 視窗的標題文字。
        :param progress_msgs: 執行時顯示的文字或其列表。

        :return: 這個類別沒有回傳值。(備註：執行項目的回傳值將以`callback_function`傳回)
        '''
        
        self.execute_list = execute_list
        self.args_list = args_list
        self.callback_function_list = callback_function_list
        self.prev = prev
        self.title = title
        self.progress_msgs = progress_msgs

        self.exception = None           #錯誤輸出的位置
        self.is_cancel_task = False     #使用者選擇取消任務
        self.is_done = False            #全部任務是否完成

        self.show_and_create_widget()

        self.progress_msg = "準備中"
        self.progress_var = 0

        #序列執行，依次執行內容
        def total_functions() -> None:
            for function, args, callback_function, progress_msg in zip(self.execute_list, self.args_list, self.callback_function_list, self.progress_msgs):
                self.progress_msg = progress_msg
                self.progress_var = 0

                if not isinstance(args,tuple):
                    raise Exception("Please check your args' type is tuple")

                result = function(*args,running_window = self)

                if self.exception is not None: return

                if callback_function is not None: callback_function(result)
                    
            self.is_done = True

        #單一執行
        def single_function() -> None:
            self.progress_msg = self.progress_msgs
            result = self.execute_list(*self.args_list,running_window = self)
            self.callback_function_list(result)
            
            self.is_done = True

        #確認執行項目是多個還是單個
        if isinstance(self.execute_list,Iterable):
            thread = Thread(target=total_functions,daemon=True)
        
        elif isinstance(self.execute_list, Callable):
            thread = Thread(target=single_function,daemon=True)
        
        else:
            raise Exception("Invalid types of argument 'execute_list'. ")

        thread.start()
        self.update_task()
    
    def show_and_create_widget(self) -> None:
        '''
        顯示視窗並創建物件(主線程)
        '''

        def cancel_task(): self.is_cancel_task = True

        self.toplevel = ttk.Toplevel(title=self.title,
                                     size=(450,100),
                                     resizable=(False,False),
                                     transient=self.prev)
        self.toplevel.protocol("WM_DELETE_WINDOW",cancel_task)
        
        self.label_text = ttk.StringVar(value="準備中")
        self.label = ttk.Label(master=self.toplevel,textvariable=self.label_text).pack(side="left",padx=20)

        self.progress_bar = ttk.Progressbar(master=self.toplevel,
                                            length=200,
                                            mode='determinate',
                                            maximum=100)
        self.progress_bar.pack(side="left")

        self.cancel_btn = ttk.Button(master=self.toplevel,
                                     text="取消",
                                     style="secondary",
                                     command=cancel_task)
        self.cancel_btn.pack(side="left",padx=10)
    
    def update_task(self) -> None:
        '''
        更新畫面(主線程)
        '''
        #用戶中斷處理
        if self.is_cancel_task:
            self.toplevel.destroy()
            msg.show_info(message="已中斷執行",
                          title=self.title,
                          parent=self.prev)
            return
        
        #更新畫面進度值
        self.progress_bar["value"] = self.progress_var

        #更新文字
        self.label_text.set(self.progress_msg)
        
        #擷取錯誤並彈窗顯示
        if self.exception is not None:
            msg.show_warning(message=str(self.exception),title="錯誤!",parent=self.prev)
            self.toplevel.destroy()
            return
        
        #完成任務的話就直接跳出
        if self.is_done:
            self.toplevel.destroy()
            return 
        
        self.toplevel.after(ms=50,func=self.update_task)