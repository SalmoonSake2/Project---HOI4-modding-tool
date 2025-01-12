'''
read_loc_files.py 
讀取本地化檔案
'''

import queue
import re

from pathlib import Path

from libs.enum.enums import *
from libs.interface.progress_window import Progress_window
from libs.root import Root

def read_loc_files(prev:Progress_window,root:Root) -> None:
    '''
    讀取本地化文件

    :param prev: 引用的框架
    :param root: 根視窗
    :param result_queue: 結果回傳佇列
    :param progress_queue: 進度回傳佇列
    '''
    #檢驗路徑是否存在
    if root.hoi4path is None:
        prev.expection = MISSING_PATH
        raise Exception("The path is not given in instance self.root!")

    #估計檔案數(用於進度回傳)
    loc_file_path = Path(root.hoi4path).joinpath(f"localisation/{root.user_lang}")

    #檢驗路徑是否存在
    if not loc_file_path.exists() or not loc_file_path.is_dir():
        prev.expection = INVALID_PATH
        raise FileNotFoundError("Invalid path for Heart of Iron IV or mod")

    loc_file_count = sum(1 for file in loc_file_path.rglob("*yml") if file.is_file())

    prev.localization_data = dict() #儲存輸出結果的字典

    try:
        loc_files = list(loc_file_path.rglob("*yml"))
    
    except PermissionError:
        prev.expection = PERMISSION_ERROR
        raise PermissionError(f"Do not has permission to reach path {loc_file_path}")

    #檢查是否正確取得本地化文本
    if not loc_files:
        prev.expection = NO_LOC_FILES
        raise FileNotFoundError(f"Cannot find any localisation files at {loc_file_path}. Please check your directary.")

    #依序處理每個yml檔並更新進度
    for index,loc_file in enumerate(loc_files):
        read_loc_file(prev,loc_file)
        if prev.is_cancel_task:
            break
        prev.progress_queue.put(int(((index+1)/loc_file_count)*100))
    
    if prev.is_cancel_task:
        return
    
    #輸出檔案
    prev.result_queue.put(prev.localization_data)

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
    except FileNotFoundError:
        prev.expection = FILE_NOT_FOUND
        raise FileNotFoundError(f"Cannot find the file {loc_file}")