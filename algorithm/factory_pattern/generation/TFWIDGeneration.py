from factory_pattern.interfaces.ITFGeneration import ITFGeneration 
from models.Models import FWI, FloatByRef
from utils.CommonUtils import check_same_equivalence,  diffset_combination, item_union

class TFWIDGeneration(ITFGeneration):
    def __init__(self) -> None:
        super().__init__()
        self.candidate_next = [] # Initial Cnext
        
    def candidate_generation(self, candidate_k, hash_two_of_trans, _, ttw) -> list:
        """
        Generates the next set of candidates based on the given candidate set.

        Args:
            candidate_k (list): The current candidate set.
            hash_two_of_trans (dict): A dictionary containing hash values of transaction pairs.
            _ (placeholder): Unused parameter.
            ttw (float): Total transaction weight.

        Returns:
            list: The next set of candidates.

        Note:
            This method implements an algorithm to generate the next set of candidates by combining
            the diffsets and calculating the weighted support (ws) based on certain conditions.
        """

        # Iterate over the candidates in reverse order
        for i in range(len(candidate_k) - 1, 0, -1):
            candidate_i = candidate_k[i]
            # Iterate over previous candidates in reverse order
            for j in range(i - 1, -1, -1):
                candidate_j = candidate_k[j]
                c = FWI()  # Create a new FWI object to store the next candidate

                # Check if candidate_i and candidate_j have the same equivalence
                if check_same_equivalence(candidate_i, candidate_j):
                    sum_tw = FloatByRef(0)

                    # Combine the diffsets and calculate ws based on conditions
                    if len(candidate_i.items) != 1 and len(candidate_j.items) != 1:
                        c.diffset = diffset_combination(candidate_i.diffset, candidate_j.diffset, hash_two_of_trans, sum_tw)
                        c.ws = candidate_i.ws - (sum_tw.value / ttw)
                    else:
                        c.diffset = diffset_combination(candidate_j.diffset, candidate_i.diffset, hash_two_of_trans, sum_tw)
                        c.ws = candidate_i.ws - (sum_tw.value / ttw)

                    c.items = item_union(candidate_i.items, candidate_j.items)

                    self.candidate_next.append(c)

        return self.candidate_next