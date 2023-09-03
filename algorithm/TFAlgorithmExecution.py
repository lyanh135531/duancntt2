import time
from visualize.visualization import Plotter
from models.Models import *
from utils.CommonUtils import *
from factory_pattern.generation.TFWITGeneration import TFWITGeneration
from factory_pattern.generation.TFWIDGeneration import TFWIDGeneration
from factory_pattern.generation.TFWINGeneration import TFWINGeneration
from factory_pattern.generation.TFWINPLUSGeneration import TFWINPLUSGeneration
class TFAlgorithmExecution:
    def __init__(self, ITFGeneration):
        self.writer = None
        self.start_time = 0
        self.end_time = 0
        self.fwis = []
        self.fwis_top_rank_K = []
        self.count_FWIs = 0
        self.memory_used = 0
        self.hash = {}
        self.pre = 0
        self.post = 0
        self.ITFGeneration = ITFGeneration


    def execute(self, transaction_file, weights_file, output, rank):
        """
        Executes the FWI algorithm with the given parameters.

        Args:
            transaction_file: The file containing transaction data.
            weights_file: The file containing item weights.
            output: The output file to write the results.
            rank: The desired number of top-ranked FWIs to find.

        Returns:
            None
        """

        self.writer = open(output, 'w')
        tw_of_trans = {}

        # Read the transaction database
        trans_weights_DB = read_trans_file(transaction_file)
        map_weights = read_weights_file(weights_file)

        map_ws = {}
        ttw = 0

        # Compute the total weight of each transaction and populate map_ws and tw_of_trans
        for trans_weight in trans_weights_DB.trans_weights:
            sum_tw = 0
            for item in trans_weight.items[::-1]:
                map_ws[item.name] = 0
                weight = map_weights.get(item.name)
                if weight is not None:
                    sum_tw += weight
                else:
                    print("Error: Missing item weight")

            trans_weight.tw = sum_tw / len(trans_weight.items)
            ttw += trans_weight.tw
            tw_of_trans[trans_weight.trans_id] = trans_weight.tw

        # Scan WD to compute the weighted support (ws) and diffset of each item denoted by fwi
        for item in map_ws:
            ws = 0
            diffset = []
            for trans_weight in trans_weights_DB.trans_weights:
                for item_in_trans in trans_weight.items[::-1]:
                    if item == item_in_trans.name:
                        diffset.append(trans_weight.trans_id)
                        ws += trans_weight.tw

            map_ws[item] = ws / ttw

            fwi = FWI()
            fwi.items.append(item)
            fwi.ws = map_ws[item]
            fwi.diffset = diffset
            self.fwis.append(fwi)

        # Sort fwi in weighted support ascending order to prioritize itemset with high ws
        self.fwis.sort(key=lambda x: (-x.ws, x.items[0]))

        if self.ITFGeneration in (TFWINGeneration, TFWINPLUSGeneration):
            self.hash = {self.fwis[i].items[0]: i for i in range(len(self.fwis))}
            root = WNTree()
            root.item.name = -1
            for trans_weight in trans_weights_DB.trans_weights:
                items_to_remove = []
                for j, item_j in enumerate(trans_weight.items[::-1]):
                    if item_j.name not in self.hash:
                        items_to_remove.append(j)
                    else:
                        item_j.ws = self.fwis[self.hash[item_j.name]].ws

                for j in items_to_remove[::-1]:
                    trans_weight.items.pop(len(trans_weight.items) - 1 - j)

                trans_weight.items.sort(key=lambda x: (-x.ws, x.name))
                self.add_items_to_WNTree(trans_weight, root)

            self.calculate_pre_post_values(root)
            self.generate_node_tree_information(root)

        # Calculate execution time and memory usage
        self.start_time = time.time()
        import psutil
        before_memory = psutil.Process().memory_info().rss
        self.find_FWIs(self.fwis, tw_of_trans, rank, ttw)
        after_memory = psutil.Process().memory_info().rss
        memory_usage = max((after_memory - before_memory) / (1024 * 2), 0)
        self.end_time = time.time()
        self.memory_used = memory_usage

        write_output_of_file(self.fwis_top_rank_K, self.writer, self.count_FWIs)
        type_mapping = {
            TFWITGeneration: TypeTF.TFWIT.value,
            TFWIDGeneration: TypeTF.TFWID.value,
            TFWINGeneration: TypeTF.TFWIN.value,
            TFWINPLUSGeneration: TypeTF.TFWINPLUS.value
        }

        type = type_mapping.get(self.ITFGeneration, '')
        print_stats(self.end_time, self.start_time, self.memory_used, type)
    
    def add_items_to_WNTree(self, trans_weight, root):
        """
        Adds items to a Weighted Node Tree (WNTree) based on a trans_weight object.
        
        Args:
            trans_weight: The trans_weight object containing the items to be added to the WNTree.
            root: The root node of the WNTree where the items will be added.
        """

        # Iterate over the items in trans_weight
        while trans_weight.items:
            item = trans_weight.items[0]
            trans_weight.items.pop(0)

            flag = False
            node = WNTree()

            # Check if the item already exists as a child node of the root
            for i in range(len(root.child_nodes)):
                if root.child_nodes[i].item.name == item.name:
                    # If it exists, update its tw (trans_weight) value
                    root.child_nodes[i].tw += trans_weight.tw
                    node = root.child_nodes[i]
                    flag = True
                    break

            # If the item does not exist as a child node, create a new node and add it to the root's child nodes
            if not flag:
                node.item = item
                node.tw = trans_weight.tw
                root.child_nodes.append(node)

            # Recursively add the remaining items to the WNTree, using the current node as the new root
            self.add_items_to_WNTree(trans_weight, node)

    def calculate_pre_post_values(self, root):
        """
        Calculates pre-order and post-order values for the nodes in a tree rooted at 'root'.
        Assigns pre-order value to 'root.pre_value' and post-order value to 'root.post_value'.
        Uses 'self.pre' and 'self.post' as counters to keep track of the values.

        Args:
            root: The root node of the tree for which pre-order and post-order values will be calculated.
        """

        # Assign pre-order value to the root node
        root.pre_value = self.pre
        self.pre += 1

        # Recursively calculate pre-order and post-order values for child nodes
        for i in range(len(root.child_nodes)):
            self.calculate_pre_post_values(root.child_nodes[i])

        # Assign post-order value to the root node
        root.post_value = self.post
        self.post += 1
    
    def generate_node_tree_information(self, root):
        """
        Generates node tree information for a given tree rooted at 'root'.
        Adds information about each node to the corresponding NodeTree object in 'self.fwis' based on 'root.item.name'.
        Uses 'self.hash' to retrieve the index of the NodeTree object in 'self.fwis'.

        Args:
            root: The root node of the tree for which node tree information will be generated.
        """

        # Check if the root node has a valid 'item.name'
        if root.item.name != -1:
            # Retrieve the index of the NodeTree object in 'self.fwis' based on 'root.item.name'
            stt = self.hash[root.item.name]
            
            # Create a new NodeTree object and assign pre-order, post-order, and tw values
            nc = NodeTree()
            nc.pre_value = root.pre_value
            nc.post_value = root.post_value
            nc.tw = root.tw
        
            # Append the new NodeTree object to the 'nodes' list of the corresponding NodeTree in 'self.fwis'
            self.fwis[stt].nodes.append(nc)

        # Recursively generate node tree information for child nodes
        for node in root.child_nodes:
            self.generate_node_tree_information(node)

    def find_FWIs(self, fwi, tw_of_trans, rank, ttw):
        """
        Finds the frequent weighted items (FWIs) based on the given parameters.

        Args:
            fwi: The list of frequent weighted items.
            tw_of_trans: The total weight of transactions.
            rank: The desired number of top-ranked FWIs to find.
            ttw: The threshold total weight.

        Returns:
            None
        """

        candidateK = []  # Initial Ck

        # Iterate through fwi list
        for i in range(len(fwi)):
            # Check if TR.count > 0 and TR.last_entry.ws = fwi[j].ws
            if len(self.fwis_top_rank_K) > 0 and round(self.fwis_top_rank_K[-1].ws, 2) == round(fwi[i].ws,2):
                # Add fwi[j] to TR.last_entry.list and fwi[j] to Ck
                self.fwis_top_rank_K[-1].list_fwis.append(fwi[i])
                candidateK.append(fwi[i])
            else:
                # Create a new rank R, R.ws = fwi[j].ws, and R.list.add(fwi[j])
                if len(self.fwis_top_rank_K) == rank:
                    break
                r = TopRankSet()
                r.ws = fwi[i].ws
                r.list_fwis.append(fwi[i])
                self.fwis_top_rank_K.append(r)
                # Add R to TR and fwi[j] to Ck
                candidateK.append(fwi[i])

        threshold = self.fwis_top_rank_K[-1].ws

        # While Ck is not null
        while len(candidateK) > 0:
            # Generate candidate items C using TFWIT_CandidateGen(Cy)
            candidate = self.ITFGeneration().candidate_generation(candidateK, tw_of_trans, threshold, ttw)
            # Sort C in weighted support ascending order
            candidate.sort(key=lambda fwi: fwi.ws, reverse=True)
            # Reset Ck, i, and j
            candidateK = []
            i = 0
            j = 0
            # Iterate through C and TR
            while j < len(candidate) and i < len(self.fwis_top_rank_K):
                # If TR[x].ws = C[i].ws
                if round(self.fwis_top_rank_K[i].ws,2) == round(candidate[j].ws,2):
                    # Add C[j] to TR[x].list and C[j] to Ck
                    self.fwis_top_rank_K[i].list_fwis.append(candidate[j])
                    candidateK.append(candidate[j])
                    j += 1
                # Else if TR[x].ws > C[j].ws
                elif candidate[j].ws > self.fwis_top_rank_K[i].ws:
                    # Create a new rank R, R.ws = C[j].ws, and R.list.add(C[j])
                    r = TopRankSet()
                    r.ws = candidate[j].ws
                    r.list_fwis.append(candidate[j])
                    # Insert R to TR at position x
                    self.fwis_top_rank_K.insert(i, r)
                    # If TR.count > k
                    if len(self.fwis_top_rank_K) > rank:
                        # Remove the last tuple in TR
                        self.fwis_top_rank_K.pop()
                        threshold = self.fwis_top_rank_K[-1].ws
                    # Add C[i] to Ck
                    candidateK.append(candidate[j])
                    j += 1
                else:
                    i += 1

            # Check if TR.count < rank and C.count > 0
            if len(self.fwis_top_rank_K) < rank and len(candidate) > 0:
                # Calculate the number of ranks to add
                z = min(rank - len(self.fwis_top_rank_K), len(candidate) - j + 1)
                # Iterate through the remaining candidate items
                for i in range(j, j + z):
                    r = TopRankSet()
                    # Create a new rank R, R.ws = C[x].ws, and R.list.add(C[x])
                    r.ws = candidate[i].ws
                    r.list_fwis.append(candidate[i])
                    # Add R to TR
                    self.fwis_top_rank_K.append(r)


if __name__ == "__main__":
    ranks = [1, 2, 3, 4, 5]
    TFWIT_time = []
    TFWID_time = []
    TFWIN_time = []
    TFWINPLUS_time = []
    TFWIT_memories_used = []
    TFWID_memories_used = []
    TFWIN_memories_used = []
    TFWINPLUS_memories_used = []
    for rank in ranks:
        tfwit = TFAlgorithmExecution(TFWITGeneration)
        tfwit.execute("../data/trans.txt", "../data/weights.txt", "../data/TFWIT_output.txt", rank)
        TFWIT_time.append(tfwit.end_time - tfwit.start_time)
        TFWIT_memories_used.append(tfwit.memory_used)

        tfwid = TFAlgorithmExecution(TFWIDGeneration)
        tfwid.execute("../data/trans.txt", "../data/weights.txt", "../data/TFWID_output.txt", rank)
        TFWID_time.append(tfwid.end_time - tfwid.start_time)
        TFWID_memories_used.append(tfwid.memory_used)

        tfwin = TFAlgorithmExecution(TFWINGeneration)
        tfwin.execute("../data/trans.txt", "../data/weights.txt", "../data/TFWIN_output.txt", rank)
        TFWIN_time.append(tfwin.end_time - tfwin.start_time)
        TFWIN_memories_used.append(tfwin.memory_used)

        tfwinplus = TFAlgorithmExecution(TFWINPLUSGeneration)
        tfwinplus.execute("../data/trans.txt", "../data/weights.txt", "../data/TFWINPLUS_output.txt", rank)
        TFWINPLUS_time.append(tfwinplus.end_time - tfwinplus.start_time)
        TFWINPLUS_memories_used.append(tfwinplus.memory_used)
        
    # Tạo một đối tượng Plotter
    plotter = Plotter(ranks, TFWID_time, TFWIT_time, TFWIN_time, TFWINPLUS_time, TFWID_memories_used, TFWIT_memories_used, TFWIN_memories_used, TFWINPLUS_memories_used)

    # Vẽ biểu đồ thời gian và lưu vào file ảnh
    plotter.draw_time_plot()

    # Vẽ biểu đồ bộ nhớ và lưu vào file ảnh
    plotter.draw_memory_plot()
