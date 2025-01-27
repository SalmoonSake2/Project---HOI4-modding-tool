
from os.path import abspath
from typing import Literal

class PDXstatement:
    '''
    說明
    ---------------------------------------------
    儲存一句完整的pdxscript 陳述句，如  
    >>> name = GER_oppose_hitler_shortcut
    >>> size > 0
    >>> add_building_construction = {
    >>>     type = industrial_complex
    >>>     level = 1
    >>>     instant_build = yes
    >>> }

    其包含兩個屬性：keyword和value。\n
    使用時可以用__init__()方法創建。
    '''
    
    Operator = Literal["=",">","<"]

    def __init__(self,keyword:str, value:str, operator:Operator = "#E") -> None:
        self.keyword = keyword
        self.value = value
        self.operator = operator
    
    def __repr__(self) -> str:
        symbols = {"#E":"=","#S":"<","#G":">"}
        return self.keyword + " " + symbols[self.operator] + " " +str(self.value)
            
    
    def __eq__(self,other) -> bool:
        if not isinstance(other,PDXstatement):
            return self.value == other
        else:
            return (self.keyword == other.keyword and
                    self.value == other.value and
                    self.operator == other.operator)
    
    def __getitem__(self, key):

        if not isinstance(self.value,list):
            return
        #依序尋找
        for statement in self.value:
            if statement.keyword == key:

                #對於value是script類型(list[PDXStatement])，提供方便進入下一層的接口
                if len(statement.value) > 0:
                    if isinstance(statement.value[0],PDXstatement):
                        return PDXstatement(statement.keyword,statement.value)
                
                return statement.value
        return

def read(path:str) -> list['PDXstatement']:
    '''
    讀取`path`位置的pdxscript檔案，輸出成statement的list
    '''

    #讀取檔案寫入記憶體
    raw_file:list[str] = list()

    try:
        with open(abspath(path),mode="r",encoding="utf-8-sig") as file:
            for line in file:
                raw_file.append(line)
    except UnicodeDecodeError:
        with open(abspath(path),mode="r",encoding="latin1") as file:
            for line in file:
                raw_file.append(line)
    
    #token化
    tokens:list[str] = list()   #最後輸出的token
    text_buffer = ""            #拼字版
    in_text = False             #檢查位置是否在引號中
    has_backslash = False       #前者是否為跳脫字元

    #逐行讀取原始檔案
    for line in raw_file:

        #逐字讀取行
        for char in line:

            #如果是換行或是註解，則跳至下一行病新增紀錄的token
            if char in "\n#": 
                if len(text_buffer): tokens.append(text_buffer)
                text_buffer = ""
                break
            
            #對於空白、tab則確認是否在引號內，若否，則新增紀錄的token
            elif char in " \t" and not in_text: 
                if len(text_buffer): tokens.append(text_buffer)
                text_buffer = ""
                continue
            
            #對於特殊token進行配對並新增紀錄的token
            elif char in "=<>{}":
                if len(text_buffer): tokens.append(text_buffer)
                text_buffer = ""
                match char:
                    case "=": tokens.append("#E")
                    case "<": tokens.append("#S")
                    case ">": tokens.append("#G")
                    case "{": tokens.append("#L")
                    case "}": tokens.append("#R")
            
            #對於引號進行檢查
            elif char == "\"":

                #若是跳脫字元，則忽略此次效果並消去反斜線效果
                if has_backslash: 
                    has_backslash = False   
                    text_buffer += char
                else: 
                    in_text = not in_text
                    text_buffer += char
            
            #對於反斜線進行檢查
            elif char == "\\":
                has_backslash = True
                text_buffer += char
            
            else:
                text_buffer += char
    
    #回收資源
    del text_buffer, in_text, has_backslash, raw_file, line, char

    #statement化
    statements:list[PDXstatement] = list()  #最後輸出的statement
    state = "k"                             #讀取狀態，k 代表keyword, v代表value, l代表list
    counter = 0                             #當前讀取的token在statement的位置
    array = []                              #讀取到列表資料時暫存的地方

    #依序讀取token
    for token in tokens:

        #如果讀取到第二個位置但不是操作符或右括號，則判定為列表
        if counter == 1 and token not in "#E#S#G#R":
            state = "l"
            array.append(keyword)
            array.append(token)

        #如果讀取到操作符，則將狀態切換至value模式
        elif token in "#E#S#G":
            operator = token
            state = "v"
        
        #如果讀取到右括號，將狀態切回keyword模式
        elif token == "#R":
            state = "k"

            #如果對於只有一項的列表，則將先前當成keyword的內容轉至array
            if counter == 1:
                array.append(keyword)

            #如果array有東西，則創建一個列表型statment，否則創建一般型R statment
            if len(array):
                statements.append(PDXstatement("#A",array))
                array = []
            else:
                statements.append(PDXstatement("#R","#R"))
            counter = -1

        #如果狀態為keyword，則將讀取到的token作為keyword紀錄
        elif state == "k":
            keyword = token
        
        #如果狀態為value，則創建一個一般型statement
        elif state == "v":
            statements.append(PDXstatement(keyword,token,operator))
            counter = -1
            state = "k"
        
        #如果狀態是list，則將讀取到的token加入array
        elif state == "l":
            array.append(token)
        
        counter += 1

    #回收資源
    del tokens, state, counter, array, keyword, operator, token, file

    #樹狀化
    current_stack = []  #當前層級中的平行statments
    stack = []          #current_stack的上級statements，每一項代表一層，每一層中則可能存在多個statements

    #逐行處理statement
    for statement in statements:

        #如果當前statement屬於L statement，則在加入該statement後將整個current_stack的物件移置stack
        if statement.value == "#L":
            current_stack.append(PDXstatement(statement.keyword,""))
            stack.append(current_stack)
            current_stack = []
        
        #如果是一般statement，則加入current_stack
        elif statement.keyword not in  "#A#R":
            current_stack.append(statement)

        #如果是列表，則在預處理後加入stack最後一項並將其作為current_stack
        elif statement.keyword == "#A":

            #預處理列表
            array= []
            statement_array = statement.value
            for element in statement_array:
                try:
                    array.append(int(element))

                except:
                    try:
                        array.append(float(element))

                    except:
                        array.append(element)

            last_stack = stack.pop()
            last_stack[-1].value = array
            current_stack = last_stack

        #如果是R statement，加入stack最後一項並將其作為current_stack
        elif statement.keyword == "#R":
            last_stack = stack.pop()
            last_stack[-1].value = current_stack
            current_stack = last_stack

    return current_stack