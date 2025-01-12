
from libs.pdxscript.pdxscript_convert import PDXstatement
from libs.enum.modifiers import modifiers as cmodifiers

def get_number(x:float|int) -> str:
    if isinstance(x,float):
        return str(("+" if x > 0 else "")+str(int(x*100))+"%")
    elif isinstance(x,int):
        return str(("+" if x > 0 else "")+str(x))
    else:
        return str(x)

def listring(iterable) -> str:
    '''
    用來將iterable的內容轉為字串
    '''
    result = ""
    for element in iterable:
        result = result + str(element) + "、"
    
    return result.rstrip("、")

def get_effect_string(effect_list:list[PDXstatement]) -> str:
    '''
    獲取效果字串
    '''
    effect_strings = list()
    for effect_statement in effect_list:
        effect_strings.append(cmodifiers[effect_statement.keyword.lower()]+get_number(effect_statement.value))
    
    return listring(effect_strings)