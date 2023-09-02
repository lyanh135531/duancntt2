class Item:
    def __init__(self):
        self.name = 0
        self.ws = 0

class Transaction_Weight:
    def __init__(self):
        self.trans_id = 0
        self.items = []

class Transaction_Weights_DB:
    def __init__(self):
        self.trans_weights = []


class TopRankSet:
    def __init__(self):
        self.ws = 0.0
        self.list_fwis = []


class FloatByRef:
    def __init__(self, value):
        self.value = value

class FWI:
    def __init__(self):
        self.items = []
        self.ws = 0.0
        self.diffset = []
        self.nodes = []

class NodeTree:
    def __init__(self):
        self.pre_value = 0
        self.post_value = 0
        self.tw = 0

class WNTree:
    def __init__(self):
        self.item = Item()
        self.tw = 0
        self.pre_value = 0
        self.post_value = 0
        self.child_nodes = []

from enum import Enum
class TypeTF(Enum):
    TFWIT = "TFWIT"
    TFWID = "TFWID"
    TFWIN = "TFWIN"
    TFWINPLUS = "TFWINPLUS"