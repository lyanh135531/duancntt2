from factory_pattern.interfaces.ITFGeneration import ITFGeneration 
from models.Models import FWI, FloatByRef
from utils.CommonUtils import *

class TFWINGeneration(ITFGeneration):
    def __init__(self) -> None:
        super().__init__()
        self.candidate_next = [] # Initial Cnext
        
    def candidate_generation(self, candidate_k, _, threshold, ttw) -> list:
        """
        Generates the next set of candidates based on the given candidate set.

        Args:
            candidate_k (list): The current candidate set.
            _ (placeholder): Unused parameter.
            threshold (float): The minimum threshold for weighted support.
            ttw (float): Total transaction weight.

        Returns:
            list: The next set of candidates.

        Note:
            This method implements an algorithm to generate the next set of candidates by combining
            the nodes, calculating the weighted support (ws), and filtering candidates based on the threshold.
        """
        for i in range(len(candidate_k) -1, 0, -1):
            candidate_i = candidate_k[i]
            for j in range(i -1, -1, -1):
                candidate_j = candidate_k[j]
                c = FWI()
                if check_same_equivalence(candidate_i, candidate_j):
                    sum_tw = FloatByRef(0)
                    c.nodes = node_code_combination(candidate_i.nodes, candidate_j.nodes, sum_tw)
                    c.ws = sum_tw.value / ttw
                    if c.ws < threshold:
                        continue
                    c.items = item_union(candidate_i.items, candidate_j.items)
                    self.candidate_next.append(c)
        return self.candidate_next