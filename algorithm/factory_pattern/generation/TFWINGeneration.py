from factory_pattern.interfaces.ITFGeneration import ITFGeneration 
from models.Models import FWI, FloatByRef
from utils.CommonUtils import *

class TFWINGeneration(ITFGeneration):
    def __init__(self) -> None:
        super().__init__()
        self.candidate_next = [] # Initial Cnext
        
    def candidate_generation(self, candidate_k, _, threshold, ttw) -> list:
        for i in range(len(candidate_k) -1, 0, -1):
            candidate_i = candidate_k[i]
            for j in range(i -1, -1, -1):
                candidate_j = candidate_k[j]
                c = FWI()
                if check_same_equivalence(candidate_i, candidate_j):
                    sumTw = FloatByRef(0)
                    c.nodes = node_code_combination(candidate_i.nodes, candidate_j.nodes, sumTw)
                    c.ws = sumTw.value / ttw
                    if c.ws < threshold:
                        continue
                    c.items = item_union(candidate_i.items, candidate_j.items)
                    self.candidate_next.append(c)
        return self.candidate_next