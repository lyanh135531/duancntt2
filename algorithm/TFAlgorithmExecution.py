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
        self.writer = open(output, 'w')
        hash_tw_of_trans = {}

        # read database
        trans_weights_DB = read_trans_file(transaction_file)
        map_weights = read_weights_file(weights_file)
        
        mapWS = {}
        ttw = 0

        for i in range(len(trans_weights_DB.trans_weights)):
            sumTW = 0
            trans_weight = trans_weights_DB.trans_weights[i]
            for j in range(len(trans_weight.items)-1, -1, -1):
                item = trans_weight.items[j].name
                mapWS[item] = 0
                weight = map_weights.get(item)

                if weight is not None:
                    sumTW += weight
                else:
                    print("Error: Missing item weight")
            
            # Definition 1
            trans_weight.tw = sumTW / len(trans_weight.items)
            # Definition 2
            ttw += trans_weight.tw
            # Definition 3
            hash_tw_of_trans[trans_weight.transID] = trans_weight.tw
        
        # Scan WD to compute the weighted support (ws) and difset of each item denoted by fwi
        for item, ws in mapWS.items():
            ws = 0
            diffset = []
            for i in range(len(trans_weights_DB.trans_weights)):
                trans_weight = trans_weights_DB.trans_weights[i]
                for j in range(len(trans_weight.items)-1, -1, -1):
                    item_in_trans = trans_weight.items[j].name
                    if item == item_in_trans:
                        diffset.append(trans_weight.transID)
                        tw = trans_weight.tw
                        ws += tw
            
            mapWS[item] = ws / ttw
            
            fwi = FWI()
            fwi.items.append(item)
            fwi.ws = mapWS[item]
            fwi.diffset = diffset
            self.fwis.append(fwi)
        # Sort fwi in weighted support ascending order to prioritize itemset with high ws
        self.fwis.sort(key=lambda x: (-x.ws, x.items[0]))
        if self.ITFGeneration is TFWINGeneration or self.ITFGeneration is TFWINPLUSGeneration:
            for i in range(len(self.fwis)):
                self.hash[self.fwis[i].items[0]] = i
            root = WnNode()
            root.item.name = -1
            for i in range(len(trans_weights_DB.trans_weights)):
                trans_weight = trans_weights_DB.trans_weights[i]
                l = len(trans_weight.items) - 1
                while l >= 0:
                    itemL = trans_weight.items[l]
                    if itemL.name not in self.hash:
                        trans_weight.items.pop(l)
                    else:
                        itemL.ws = self.fwis[self.hash[itemL.name]].ws
                    l -= 1
                trans_weight.items.sort(key=lambda x: (-x.ws, x.name))
                self.insert_tree(trans_weight, root)
            self.generate_order(root)

            self.generate_nc_sets(root)

        
        # calulation time and memory execution
        self.start_time = time.time()
        import psutil
        before_memory = psutil.Process().memory_info().rss
        self.find_FWIs(self.fwis, hash_tw_of_trans, rank, ttw)
        # Lấy thông tin tài nguyên sau khi thực hiện chương trình
        after_memory = psutil.Process().memory_info().rss
        memory_usage = max((after_memory - before_memory) / (1024 * 1024), 0)
        self.end_time = time.time()
        self.memory_used = memory_usage 
        write_output_of_file(self.fwis_top_rank_K, self.writer, self.count_FWIs)
        type = ""
        if self.ITFGeneration is TFWITGeneration:
            type = TypeTF.TFWIT.value
        elif self.ITFGeneration is TFWIDGeneration:
            type = TypeTF.TFWID.value
        elif self.ITFGeneration is TFWINGeneration:
            type = TypeTF.TFWIN.value
        elif self.ITFGeneration is TFWINPLUSGeneration:
            type = TypeTF.TFWINPLUS.value
        print_stats(self.end_time, self.start_time, self.memory_used, type)
    
    def insert_tree(self, trans_weight, root):
        while trans_weight.items:
            item = trans_weight.items[0]
            trans_weight.items.pop(0)

            flag = False
            node = WnNode()

            for i in range(len(root.child_nodes)):
                if root.child_nodes[i].item.name == item.name:
                    root.child_nodes[i].tw += trans_weight.tw
                    node = root.child_nodes[i]
                    flag = True
                    break
            if not flag:
                node.item = item
                node.tw = trans_weight.tw
                root.child_nodes.append(node)
            self.insert_tree(trans_weight, node)
    
    def generate_nc_sets(self, root):
        if root.item.name != -1:
            stt = self.hash[root.item.name]
            
            nc = NodeCode()
            nc.pre_value = root.pre_value
            nc.post_value = root.post_value
            nc.tw = root.tw
           
            self.fwis[stt].nodes.append(nc)

        for node in root.child_nodes:
            self.generate_nc_sets(node)

    def generate_order(self, root):
        root.pre_value = self.pre
        self.pre += 1
        for i in range(len(root.child_nodes)):
            self.generate_order(root.child_nodes[i])
        root.post_value = self.post
        self.post += 1

    def find_FWIs(self, fwi, hash_tw_of_trans, rank, ttw):
        candidateK = [] # Initial Ck
        # for j = 0 to fwi.count - 1 do
        for i in range(len(fwi)):
            # If TR.count > 0 and TR.last_entry.ws = fwi[j].ws then
            if len(self.fwis_top_rank_K) > 0 and self.fwis_top_rank_K[-1].ws == fwi[i].ws:
                #  Add fwi[j] to TR.last_entry.list and fwi[j] to Ck
                self.fwis_top_rank_K[-1].list_fwis.append(fwi[i])
                candidateK.append(fwi[i])
            # Let R is new rank, R.ws = fwi[j].ws and R.list.add(fwi[j])  
            else:
                if len(self.fwis_top_rank_K) == rank:
                    break
                r = TRset()
                r.ws = fwi[i].ws
                r.list_fwis.append(fwi[i])
                self.fwis_top_rank_K.append(r)
                # Add R to TR and fwi[j] to Ck
                candidateK.append(fwi[i])
        # end for

        threshold = self.fwis_top_rank_K[-1].ws

        #While Ck # null & do
        while len(candidateK) > 0:
            # C « TFWIT_CandidateGen(Cy)
            candidate = self.ITFGeneration().candidate_generation(candidateK, hash_tw_of_trans, threshold, ttw)
            # Sort C in weighted support ascending order
            candidate.sort(key=lambda fwi: fwi.ws, reverse=True)
            # Ck <- 0; i <- 0; j < = 0
            candidateK = []
            i = 0
            j = 0
            # While j < C.count and x < TR.count do
            while j < len(candidate) and i < len(self.fwis_top_rank_K):
                # If TR[x].ws = C[i].ws then
                if self.fwis_top_rank_K[i].ws == candidate[j].ws:
                    # Add C[j] to TR[x].list and C[j] to Ck
                    self.fwis_top_rank_K[i].list_fwis.append(candidate[j])
                    candidateK.append(candidate[j])
                    j += 1
                # Else if TR[x].ws > C[j].ws then
                elif candidate[j].ws > self.fwis_top_rank_K[i].ws:
                    # Let R be the new rank, R.ws = C[j].ws and R.list.add(C[j])
                    r = TRset()
                    r.ws = candidate[j].ws
                    r.list_fwis.append(candidate[j])
                    # Insert R to TR at position x
                    self.fwis_top_rank_K.insert(i, r)
                    # If TR.count > k then
                    if len(self.fwis_top_rank_K) > rank:
                        # Remove the last tuple in TR
                        self.fwis_top_rank_K.pop()
                        threshold = self.fwis_top_rank_K[-1].ws
                    # Add C[i] to Ck
                    candidateK.append(candidate[j])
                    j += 1
                else:
                    i += 1
            
            if len(self.fwis_top_rank_K) < rank and len(candidate) > 0:
                # Let t «— min(k — TR.count, C.count - l + 1)
                z = min(rank - len(self.fwis_top_rank_K), len(candidate) - j + 1)
                # For (x=1; x<l+t; x++) do
                for i in range(j, j + z):
                    r = TRset()
                    # R.ws = C[x].ws and R.list.add(C[x])
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
        tfwit.execute("./data/chess_trans.txt", "./data/chess_pro.txt", "./data/TFWIT_output.txt", rank)
        #tfwit.execute("./data/trans.txt", "./data/weights.txt", "./data/TFWIT_output.txt", i)
        TFWIT_time.append(tfwit.end_time - tfwit.start_time)
        TFWIT_memories_used.append(tfwit.memory_used)

        tfwid = TFAlgorithmExecution(TFWIDGeneration)
        tfwid.execute("./data/chess_trans.txt", "./data/chess_pro.txt", "./data/TFWID_output.txt", rank)
        TFWID_time.append(tfwid.end_time - tfwid.start_time)
        TFWID_memories_used.append(tfwid.memory_used)

        tfwin = TFAlgorithmExecution(TFWINGeneration)
        tfwin.execute("./data/trans.txt", "./data/weights.txt", "./data/TFWIT_output.txt", rank)
        TFWIN_time.append(tfwin.end_time - tfwin.start_time)
        TFWIN_memories_used.append(tfwin.memory_used)

        tfwinplus = TFAlgorithmExecution(TFWINPLUSGeneration)
        tfwinplus.execute("./data/chess_trans.txt", "./data/chess_pro.txt", "./data/TFWINPLUS_output.txt", rank)
        TFWINPLUS_time.append(tfwinplus.end_time - tfwinplus.start_time)
        TFWINPLUS_memories_used.append(tfwinplus.memory_used)
        
    # Tạo một đối tượng Plotter
    plotter = Plotter(ranks, TFWID_time, TFWIT_time, TFWIN_time, TFWINPLUS_time, TFWID_memories_used, TFWIT_memories_used, TFWIN_memories_used, TFWINPLUS_memories_used)

    # Vẽ biểu đồ thời gian và lưu vào file ảnh
    plotter.draw_time_plot()

    # Vẽ biểu đồ bộ nhớ và lưu vào file ảnh
    #plotter.draw_memory_plot()
