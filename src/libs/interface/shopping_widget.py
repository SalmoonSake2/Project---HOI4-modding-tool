'''
shopping_widget.py

author: Salmoon Sake
購物清單物件
'''

from typing import Callable, Iterable, Literal
import ttkbootstrap as _ttk
from ttkbootstrap.dialogs import Messagebox as msg

class Shoppinglist(_ttk.Frame):
    '''
    購物清單物件
    '''
    def __init__(self,
                 mode:Literal["label","combobox","entry"] = "label",
                 allow_spinbox:bool = False,
                 item_length_limit:int | None = 20,
                 spinbox_limit:tuple[int,int] = (0,100),
                 **kwargs) -> None:
        '''
        :param mode: 展示物件的形式，label代表一般標籤，無法更改。combobox是下拉式選單，可以選擇當中的選項，由set_avalible_items()設定。entry則是一般文字輸入。
        :param allow_spinbox: 是否使用spinbox設定數量
        :param item_length_limit: 清單的項目上限
        :param spinbox_limit: spinbox的數量上下界
        '''
        super().__init__(**kwargs)

        #outlook
        self.item_frame = _ttk.Frame(master=self)
        self.addon_button = _ttk.Button(master=self,text="+",style=(_ttk.OUTLINE,_ttk.SECONDARY),width=1)
        self.item_object = list()

        self.item_frame.grid(row=0,column=0)
        self.addon_button.grid(row=0,column=1)

        #data
        self.mode = mode
        self.allow_spinbox = allow_spinbox
        self.item_length_limit = item_length_limit
        self.spinbox_limit = spinbox_limit

        self.item_list:list[str] = list()
        self.item_count_list:list[int] = list()
        
        self._combobox_items = None
    
    def addon_command(self,command:Callable) -> None:
        '''
        按下新增按鈕後的操作，建議在command中添加append()模塊
        '''
        self.addon_button.config(command=command)

    def set_avalible_items(self,items:Iterable) -> None:
        '''
        設置下拉式選單的選項
        '''
        self._combobox_items = items

    def set_item(self,item_list:list[str],item_count_list:list[int]=None) -> None:
        self.item_list = list(item_list[:])
        if self.allow_spinbox: self.item_count_list = list(item_count_list[:])
        if self.allow_spinbox and item_count_list is None: raise Exception("if you are using spinbox, set_item() method shall include item_count_list")
        if self.allow_spinbox and len(item_list) != len(item_count_list): raise Exception("these two list are no the same length")
        self._refresh()
    
    def get_item(self) -> list[str] | list[tuple[str,int]]:
        if self.allow_spinbox:
            return zip(self.item_list, self.item_count_list)
        else:
            return self.item_list
    
    def clear_item(self) -> None:
        self.item_list.clear()
        if self.allow_spinbox:self.item_count_list.clear()
        self._refresh()
    
    def pop_item(self,index:int) -> None:
        self.item_list.pop(index)
        if self.allow_spinbox: self.item_count_list.pop(index)
        self._refresh()
    
    def append_item(self,item:str,count:int=None) -> None:

        if len(self.item_list) < self.item_length_limit:
            self.item_list.append(item)
            if self.allow_spinbox: self.item_count_list.append(count)
            self._refresh()

        else:
            msg.show_warning(message="數量已達上限",title="提示")
    
    def _refresh(self) -> None:

        #移除舊的物件
        self.item_frame.destroy()
        self.item_frame = _ttk.Frame(master=self)    #包覆所有項目的框
        self.item_frame.grid(row=0,column=0)

        self.item_object_frame = list() #單一項目的眶

        #繪製
        for index, item in enumerate(self.item_list):

            self.item_object_frame.append(_ttk.Frame(master=self.item_frame,relief=_ttk.SOLID,borderwidth=1))

            if self.mode == "label":
                self.item_object_frame[index].showobj = _ttk.Label(master=self.item_object_frame[index],text=item)
            
            elif self.mode == "combobox":
                self.item_object_frame[index].showobj = _ttk.Combobox(master=self.item_object_frame[index],state=_ttk.READONLY,width=4,values=self._combobox_items)
                self.item_object_frame[index].var = _ttk.StringVar(value=item)
                self.item_object_frame[index].var.trace_add("write",lambda a,b,c,x=index:self._on_combobox_select(x))
                self.item_object_frame[index].showobj.config(textvariable=self.item_object_frame[index].var)
            
            elif self.mode == "entry":
                self.item_object_frame[index].showobj = _ttk.Entry(master=self.item_object_frame[index],width=4)
                self.item_object_frame[index].var = _ttk.StringVar(value=item)
                self.item_object_frame[index].var.trace_add("write",lambda a,b,c,x=index:self._on_combobox_select(x))
                self.item_object_frame[index].showobj.config(textvariable=self.item_object_frame[index].var)
            
            else:
                raise Exception("Unknown mode! The mode can only be these args: label, combobox, entry")

            if self.allow_spinbox:
                self.item_object_frame[index].spinbox = _ttk.Spinbox(master=self.item_object_frame[index],
                                                                     from_=self.spinbox_limit[0],
                                                                     to=self.spinbox_limit[1],
                                                                     width=2)
                
                self.item_object_frame[index].spinbox.var = _ttk.StringVar(value=self.item_count_list[index])
                self.item_object_frame[index].spinbox.var.trace_add("write",lambda a,b,c,x=index:self._on_combobox_select(x))
                self.item_object_frame[index].spinbox.config(textvariable=self.item_object_frame[index].spinbox.var)

            self.item_object_frame[index].pop_btn = _ttk.Button(master=self.item_object_frame[index],text="x",command=lambda x=index:self.pop_item(x), style=(_ttk.LINK,_ttk.DANGER))

            self.item_object_frame[index].pack(side=_ttk.LEFT,padx=5)
            self.item_object_frame[index].showobj.pack(side=_ttk.LEFT,padx=5,pady=1)
            if self.allow_spinbox: self.item_object_frame[index].spinbox.pack(side=_ttk.LEFT,pady=1)
            self.item_object_frame[index].pop_btn.pack(side=_ttk.LEFT,pady=1)
            self.item_object.append(self.item_object_frame[index])
    
    def _on_combobox_select(self,index) -> None:
        self.item_list[index] = self.item_object_frame[index].var.get()
        if self.allow_spinbox: self.item_count_list[index] = self.item_object_frame[index].spinbox.var.get()

del _ttk, Callable, Iterable, Literal, msg
