from models.Models import *

def check_same_equivalence(cI, cJ):
        if len(cI.items) == 1 and len(cJ.items) == 1:
            return True
        else:
            i = 0
            j = 0
            flag = True
            while i < len(cI.items) - 1 and j < len(cJ.items) - 1:
                if cI.items[i] != cJ.items[j]:
                    flag = False
                    break
                i += 1
                j += 1

            return flag

def tidset_combination(first_diffset, second_diffset, hash_tw_of_trans, sum_tw):
    result = []
    for item in first_diffset:
        for item2 in second_diffset:
            if (item == item2):
                result.append(item)
                sum_tw.value += hash_tw_of_trans[item]
                break
    return result

def diffset_combination(candidate_i, candidate_j, hash_tw_of_trans, sumTw):
    result = []
    for j in range(len(candidate_j)):
        diff = True
        cJ = candidate_j[j]
        for i in range(len(candidate_i)):
            cI = candidate_i[i]
            if cJ == cI:
                diff = False
                break
        if diff:
            result.append(cJ)
            sumTw.value += hash_tw_of_trans[cJ]
    return result

def node_code_combination(a, b, sumTw):
    result = []
    for bJ in b:
        for aI in a:
            if bJ.pre_value < aI.pre_value and bJ.post_value > aI.post_value:
                if result and result[-1].pre_value == bJ.pre_value and result[-1].post_value == bJ.post_value:
                    result[-1].tw += aI.tw
                else:
                    temp = NodeCode()
                    temp.pre_value = bJ.pre_value
                    temp.post_value = bJ.post_value
                    temp.tw = aI.tw
                    result.append(temp)
                sumTw.value += aI.tw
    return result

    
def item_union(a, b):
    result = a[:]
    result.append(b[-1])
    return result


def read_trans_file(filename):
    trans_weights_DB = Transaction_Weights_DB()

    with open(filename, 'r') as file:
        lines = file.readlines()

        i = 0
        for line in lines:
            trans_weight = Transaction_Weight()
            trans_weight.transID = i + 1

            lineSplited = line.split(" ")

            for itemString in lineSplited:
                item = Item()
                try:
                    item.name = int(itemString)
                except:
                    continue
                trans_weight.items.append(item)
            trans_weights_DB.trans_weights.append(trans_weight)
            i += 1

    return trans_weights_DB

def read_weights_file(filename):
    map_weights = {}
    with open(filename, 'r') as file:
        lines = file.readlines()

        item = 0
        for line in lines:
            map_weights[item + 1] = float(line)
            item += 1

    return map_weights

def write_output_of_file(fwis_top_rank_k, writer, count_FWIs):
    header = f"+{'-' * 10}+{'-' * 90}+{'-' * 20}+\n"
    writer.write(header)
    header_values = f"|{'Rank':<10}|{'Itemset':<90}|{'Ws':<20}|\n"
    writer.write(header_values)
    header_line = f"+{'=' * 10}+{'=' * 90}+{'=' * 20}+\n"
    writer.write(header_line)
    
    for i in range(len(fwis_top_rank_k)):
        item = ''
        for fwi in fwis_top_rank_k[i].list_fwis:
            item += f"{fwi.items} "
            count_FWIs += 1
        values = f"|{i+1:<10}|{item:<90}|{fwis_top_rank_k[i].ws:<2}|\n"
        writer.write(values)
        
        line = f"+{'-' * 10}+{'-' * 90}+{'-' * 20}+\n"
        writer.write(line)
        
    writer.close()

def print_stats(end_time , start_time, memory_used, typeTF):
    print("========== ", typeTF ,"- STATUS ============")
    print(" Total time ~:", end_time - start_time, "ms")
    print(" Max memory:", memory_used / 1024 * 1024, "MB")
    print("==========================================")