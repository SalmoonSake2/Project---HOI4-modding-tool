'''
read_loc_files.py 
讀取本地化檔案
'''

import re

from pathlib import Path

from libs.enum.enums import *
from libs.interface.running_window import RunningWindow
from libs.root import Root

def read_loc_files(root:Root,running_window:RunningWindow) -> None:
    '''
    讀取本地化文件

    :param prev: 引用的框架
    :param root: 根視窗
    :param result_queue: 結果回傳佇列
    :param progress_queue: 進度回傳佇列
    '''
    #檢驗路徑是否存在
    if root.hoi4path is None:
        running_window.exception = "The path is not given in instance self.root!"
        return

    #估計檔案數(用於進度回傳)
    loc_file_path = Path(root.hoi4path).joinpath(f"localisation/{root.user_lang}")

    #檢驗路徑是否存在
    if not loc_file_path.exists() or not loc_file_path.is_dir():
        running_window.exception= "Invalid path for Heart of Iron IV or mod"
        return

    loc_file_count = sum(1 for file in loc_file_path.rglob("*yml") if file.is_file())

    running_window.localization_data = dict() #儲存輸出結果的字典

    try:
        loc_files = list(loc_file_path.rglob("*yml"))
    
    except PermissionError as e:
        running_window.exception = e
        return

    #檢查是否正確取得本地化文本
    if not loc_files:
        running_window.exception = f"Cannot find any localisation files at {loc_file_path}. Please check your directary."
        return 

    #依序處理每個yml檔並更新進度
    for index,loc_file in enumerate(loc_files):
        read_loc_file(running_window,loc_file)
        if running_window.is_cancel_task:
            break
        running_window.progress_var_queue.put(int(((index+1)/loc_file_count)*100))
    
    if running_window.is_cancel_task:
        return
    
    #輸出檔案
    return running_window.localization_data

def read_loc_file(prev,loc_file:str) -> None:
    '''
    讀取`loc_file`的本地化文檔

    :param prev: 引用的框架
    :param loc_file: 本地化文檔的路徑
    '''
    pattern = r'(\w+):\s*"([^"]+)"'#形如 keyword : "value"的特徵。
    try:
        with open(file=loc_file,mode="r",encoding="utf-8-sig") as file:
            for line in file:
                match = re.search(pattern, line.strip())
                if match:
                    key, value = match.groups()
                    prev.localization_data[key] = value

                if prev.is_cancel_task:
                    break
    except FileNotFoundError as e:
        prev.exception = e