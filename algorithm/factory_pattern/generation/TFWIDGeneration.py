from factory_pattern.interfaces.ITFGeneration import ITFGeneration 
from models.Models import FWI, FloatByRef
from utils.CommonUtils import check_same_equivalence,  diffset_combination, item_union

class TFWIDGeneration(ITFGeneration):
    def __init__(self) -> None:
        super().__init__()
        self.candidate_next = [] # Initial Cnext
        
    def candidate_generation(self, candidate_k, hash_two_of_trans, _, ttw) -> list:
        for i in range(len(candidate_k) -1, 0, -1):
            candidate_i = candidate_k[i]
            for j in range(i -1, -1, -1):
                candidate_j = candidate_k[j]
                c = FWI()
                if check_same_equivalence(candidate_i, candidate_j):
                    sumTw = FloatByRef(0)
                    if len(candidate_i.items) != 1 and len(candidate_j.items) != 1:
                        c.diffset = diffset_combination(candidate_i.diffset, candidate_j.diffset, hash_two_of_trans, sumTw)
                        c.ws = candidate_i.ws - (sumTw.value / ttw)
                    else:
                        c.diffset = diffset_combination(candidate_j.diffset, candidate_i.diffset, hash_two_of_trans, sumTw)
                        c.ws = candidate_i.ws - (sumTw.value / ttw)
                    c.items = item_union(candidate_i.items, candidate_j.items)
                    self.candidate_next.append(c)
        return self.candidate_next