'''
snapshot.py

快照工具，方便建立最近的操作歷史並還原。
'''

from typing import Any
from collections import deque

class Snapshot:
    '''
    快照物件
    '''
    def __init__(self,max_count:int=20) -> None:
        '''
        建立快照物件
        '''
        self._state = None
        self.undo_stack = deque(maxlen=max_count)
        self.redo_stack = deque(maxlen=max_count)
    
    def create(self,item:Any) -> None:
        self.redo_stack.clear()

        self.undo_stack.append(self._state)
        self._state = item

    def can_undo(self) -> None:
        return len(self.undo_stack) != 0

    def can_redo(self) -> None:
        return len(self.redo_stack) != 0
    
    def undo(self) -> None:

        if len(self.undo_stack) == 0: return

        self.redo_stack.append(self._state)
        self._state = self.undo_stack.pop()
        
    def redo(self) -> None:

        if len(self.redo_stack) ==0: return

        self.undo_stack.append(self._state)
        self._state = self.redo_stack.pop()
    
    def get(self) -> Any: return self._state

    def clear(self) -> None:
        self.undo_stack.clear()
        self.redo_stack.clear()
