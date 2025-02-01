'''
stringutil.py

字串實用工具
'''

def listring(iterable) -> str:
    '''
    用來將iterable的內容轉為字串
    '''
    result = ""
    for element in iterable:
        result = result + str(element) + "、"
    
    return result.rstrip("、")