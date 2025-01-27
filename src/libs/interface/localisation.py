'''
localisation.py

本地化文字
'''

from libs.root import root

def loc(key:str) -> str:
    '''
    獲取遊戲本地化字串
    '''
    try:
        return root.game_loc[key]
    
    except KeyError:
        return key