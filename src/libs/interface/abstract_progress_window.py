'''
abstract_progress_window.py
型態提示
'''

import queue
from typing import Callable

import ttkbootstrap as ttk

class Abstract_progress_window:
    def __init__(self) -> None:
        self.target:Callable
        self.args:tuple
        self.output_container = None
        self.prev:ttk.Toplevel | ttk.Window
        self.title:str
        self.progress_msg:str
        self.is_cancel_task:bool
        self.expection:None | str
        self.result_queue: queue.Queue
        self.progress_queue: queue.Queue