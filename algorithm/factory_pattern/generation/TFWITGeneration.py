from factory_pattern.interfaces.ITFGeneration import ITFGeneration 
from models.Models import FWI, FloatByRef
from utils.CommonUtils import check_same_equivalence,  tidset_combination, item_union

class TFWITGeneration(ITFGeneration):
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
                    sum_tw = FloatByRef(0)
                    c.diffset = tidset_combination(candidate_i.diffset, candidate_j.diffset, hash_two_of_trans, sum_tw)
                    c.ws = sum_tw.value / ttw
                    c.items = item_union(candidate_i.items, candidate_j.items)
                    self.candidate_next.append(c)
        return self.candidate_next