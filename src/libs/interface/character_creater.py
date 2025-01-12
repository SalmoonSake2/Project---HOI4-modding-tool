'''
建立角色需要的檔案：
<mod>
┕ common
 ┕ characters
  ┕ <file.txt>
 ┕ country_leader
  ┕ <traits.txt>
┕ gfx
 ┕ leaders
  ┕ <TAG>
   ┕ <file.dds>
┕ interface
 ┕ <file.gfx>
┕ localisation
 ┕ simp_chinese
  ┕ <file.yml>

'''

from tkinter import filedialog
from ttkbootstrap.dialogs import Messagebox as msg
from PIL import Image, ImageTk
import ttkbootstrap as ttk
import os

from libs.interface.trait_creater import Trait_creater
from libs.interface.trait_selecter import Trait_selecter

class Character_creater:
    '''
    角色創建器
    '''
    def __init__(self, root) -> None:
        self.root = root
        self.show_and_create_widget()

    def show_and_create_widget(self) -> None:
        '''
        顯示角色創建器的頁面
        '''

        toplevel = ttk.Toplevel(title="角色創建器",
                            size=(570,750),
                            transient=self.root,
                            resizable=(False,False))
        
        def create_photo(file_name:str) -> ImageTk.PhotoImage:
            '''
            建立圖檔，會從../../../assets中尋找同名的png、dds檔，並轉為tkinter可以處理的格式
            '''
            try:
                return ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), "../../../assets", f"{file_name}.png")))
            except:
                return ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), "../../../assets", f"{file_name}.dds")))
            
        def create_upper_frame() -> None:
            #建立相片及描述frame
            upper_frame = ttk.Frame(master=toplevel)
            upper_frame.pack()

            #建立名片框
            carte_frame = ttk.Frame(master=upper_frame)
            carte_frame.pack(side="left")

            #建立相片框
            photo_frame = ttk.Canvas(master=carte_frame,width=155,height=212)
            photo_frame.pack()

            #大頭貼
            def photo_button_command(args) -> None:
                file_path = filedialog.askopenfilename(title="選擇圖片",filetypes=[("Image Files","*.png;*.dds")])

                if file_path:
                    photo = ImageTk.PhotoImage(Image.open(file_path).resize((155,212)))
                else:
                    photo = ImageTk.PhotoImage(Image.open(f"{os.path.dirname(__file__)}/../../../assets/unknown_character.png"))

                photo_frame.itemconfig(photo_image_id,image= photo)
                photo_frame.photo_image = photo

            photo_frame.photo_image = create_photo("unknown_character")
            photo_image_id = photo_frame.create_image(0,0,image=photo_frame.photo_image,anchor="nw")
            photo_frame.tag_bind(photo_image_id,"<Button-1>",photo_button_command)

            #小頭貼
            def advisor_button_command(args) -> None:
                file_path = filedialog.askopenfilename(title="選擇圖片",filetypes=[("Image Files","*.png;*.dds")])

                if file_path:
                    photo = ImageTk.PhotoImage(Image.open(file_path).resize((63,66)))
                else:
                    photo = ImageTk.PhotoImage(Image.open(f"{os.path.dirname(__file__)}/../../../assets/unknown_advisor.dds"))

                photo_frame.itemconfig(advisor_image_id,image= photo)
                photo_frame.advisor_image = photo

            photo_frame.advisor_image = create_photo("unknown_advisor")
            advisor_image_id = photo_frame.create_image(92,146,image=photo_frame.advisor_image,anchor="nw")
            photo_frame.tag_bind(advisor_image_id,"<Button-1>",advisor_button_command)

            #用於顯示提示文字的函數
            def set_placeholder(entry:ttk.Entry | ttk.ScrolledText,show_text:str) -> None:
                if isinstance(entry,ttk.Entry):
                    entry.insert(0,show_text)
                    entry.config(foreground="gray")

                    def focus_in(args):
                        if entry.get() == show_text:
                            entry.delete(0,ttk.END)
                            entry.config(foreground="white")
                    
                    def focus_out(args):
                        if not entry.get():
                            entry.insert(0,show_text)
                            entry.config(foreground="gray")
                    
                    entry.bind("<FocusIn>",focus_in)
                    entry.bind("<FocusOut>",focus_out)
                
                elif isinstance(entry,ttk.ScrolledText):
                    entry.insert("1.0",show_text)
                    entry.config(fg="gray")

                    def focus_in(args):
                        if entry.get("1.0","end-1c") == show_text:
                            entry.delete("1.0","end")
                            entry.config(fg="white")
                    
                    def focus_out(args):
                        if not entry.get("1.0", "end-1c").strip():  # 檢查內容是否為空
                            entry.insert("1.0", show_text)
                            entry.config(fg="gray")
                    
                    entry.bind("<FocusIn>",focus_in)
                    entry.bind("<FocusOut>",focus_out)

            #建立名稱輸入欄
            name_entry = ttk.Entry(master=carte_frame)
            set_placeholder(name_entry,"請輸入名字")
            name_entry.pack()

            #國籍輸入欄
            country_entry = ttk.Entry(master=carte_frame)
            set_placeholder(country_entry,"請輸入國籍代碼")
            country_entry.pack()

            #建立描述輸入欄
            desc_text = ttk.ScrolledText(master=upper_frame)
            desc_text.config(height=17)
            set_placeholder(desc_text,"請輸入描述")
            desc_text.pack(side="left")

        #建立大名片Frame
        create_upper_frame()

        #建立功能tab
        notebook = ttk.Notebook(master=toplevel,height=400,width=400)
        tab_names = ("leader", "advisor", "theorist", "high_command","army_chief", "navy_chief", "air_chief", "land_leader", "navy_leader")
        tabs = {name: ttk.Frame(master=notebook) for name in tab_names}

        #領導人
        notebook.add(text="領導人",child=tabs["leader"])

        #意識形態
        ideology_frame = ttk.Frame(master=tabs["leader"])
        ideology_frame.pack(fill="x",pady=10)

        idelogies_label = ttk.Label(master=ideology_frame,text="意識形態(若為自訂型態則輸入意識形態代碼): ")
        idelogies_label.pack(side="left",padx=10)
        IDEOLOGIES = ("無",
                      "民主-保守主義",
                      "民主-自由主義",
                      "民主-社會主義",
                      "共產-馬克思主義",
                      "共產-列寧主義",
                      "共產-史達林主義",
                      "共產-反修正主義",
                      "共產-無政府共產主義",
                      "法西斯-納粹主義",
                      "法西斯-原始納粹主義",
                      "法西斯-原始法西斯主義",
                      "法西斯-長槍主義",
                      "法西斯-雷克斯主義",
                      "中立-專制主義",
                      "中立-寡頭主義",
                      "中立-溫和主義",
                      "中立-中間路線",
                      "無政府主義")
        ideology_combobox = ttk.Combobox(master=ideology_frame,values=IDEOLOGIES)
        ideology_combobox.pack(side="left")

        #特質
        trait_frame = ttk.Frame(master=tabs["leader"])
        trait_frame.pack(fill="x",pady=10)

        traits_label = ttk.Label(master=trait_frame,text="特質: ")
        traits_label.pack(side="left",padx=10)

        #TODO: 插入特質按鈕，並會自動換行。懸停時顯示效果(特質創建器)
        def trait_btn_command() -> None:
            response = msg.yesno(message="是否新建一個新的特質?",title="提示",parent=toplevel)
            if response == "Yes":
                Trait_creater(toplevel,self.root)
            
            elif response == "No":
                Trait_selecter(toplevel,self.root)

        traits_btn = ttk.Button(master=trait_frame,text="新增",style="outline",command=trait_btn_command)
        traits_btn.pack(side="left")

        #政府顧問
        notebook.add(text="政府顧問",child=tabs["advisor"])
        notebook.add(text="理論家",child=tabs["theorist"])
        notebook.add(text="最高指揮部",child=tabs["high_command"])
        notebook.add(text="陸軍顧問",child=tabs["army_chief"])
        notebook.add(text="海軍顧問",child=tabs["navy_chief"])
        notebook.add(text="空軍顧問",child=tabs["air_chief"])
        notebook.add(text="陸軍將領",child=tabs["land_leader"])
        notebook.add(text="海軍將領",child=tabs["navy_leader"])
        notebook.pack()

        #建立底部按鈕
        bottom_frame = ttk.Frame(master=toplevel)
        bottom_frame.pack(fill="x",expand=True)

        confirm_btn = ttk.Button(master=bottom_frame,text="確定")
        confirm_btn.pack(side="right",padx=10)

        cancel_btn = ttk.Button(master=bottom_frame,text="取消",style="secondary-outline")
        cancel_btn.pack(side="right",padx=10)
    