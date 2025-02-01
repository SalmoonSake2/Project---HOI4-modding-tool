'''
cache_reader.py

快取工具
註:使用者安全性干我P事? 能用方便就可以
'''

import pickle
from typing import Any

from libs.root import root

def pickle_write(data:Any,path:str):
    with open(path,"wb") as file: pickle.dump(data,file)
        
def pickle_read(path:str) -> Any:
    with open(path,"rb") as file: return pickle.load(file)

def save_cache(running_window) -> None:
    try:
        cache = (root.game_loc,root.map_data,root.game_image)
        pickle_write(cache,"data/cache.dat")
    except:
        running_window.exception = "建立快取資料出現錯誤"
        return

def load_cache(running_window=None) -> None:
    try:
        root.game_loc, root.map_data, root.game_image = pickle_read("data/cache.dat")
    except:
        running_window.exception = "讀取快取資料出現錯誤"
        return