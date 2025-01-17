'''
province.py
'''

from libs.pdxscript.pdxscript import PDXstatement

class Province:
    def __init__(self,id) -> None:
        self.id = id
        self.state = None
        self.country = None
        self.core = None
        self.name = None

class State(PDXstatement):
    ...

class StrategicRegion(PDXstatement):
    ...