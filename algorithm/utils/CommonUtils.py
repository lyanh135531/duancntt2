from models.Models import *

def check_same_equivalence(candidate_i, candidate_j):
    """
    Checks if two candidates have the same equivalence.

    Args:
        candidate_i: The first candidate.
        candidate_j: The second candidate.

    Returns:
        True if the candidates have the same equivalence, False otherwise.
    """
    if len(candidate_i.items) == 1 and len(candidate_j.items) == 1:
        return True
    else:
        i = 0
        j = 0
        flag = True
        while i < len(candidate_j.items) - 1 and j < len(candidate_j.items) - 1:
            if candidate_i.items[i] != candidate_j.items[j]:
                flag = False
                break
            i += 1
            j += 1

        return flag


def tidset_combination(first_diffset, second_diffset, hash_tw_of_trans, sum_tw):
    """
    Combines two tidsets and calculates the sum of their total weights.

    Args:
        first_diffset: The first tidset.
        second_diffset: The second tidset.
        hash_tw_of_trans: A dictionary mapping transaction IDs to their total weights.
        sum_tw: A shared value to store the sum of total weights.

    Returns:
        The combined tidset and the updated sum of total weights.
    """
    result = []
    for item in first_diffset:
        for item2 in second_diffset:
            if item == item2:
                result.append(item)
                sum_tw.value += hash_tw_of_trans[item]
                break
    return result


def diffset_combination(candidate_i, candidate_j, hash_tw_of_trans, sum_tw):
    """
    Combines two diffsets and calculates the sum of their total weights.

    Args:
        candidate_i: The first diffset.
        candidate_j: The second diffset.
        hash_tw_of_trans: A dictionary mapping transaction IDs to their total weights.
        sum_tw: A shared value to store the sum of total weights.

    Returns:
        The combined diffset and the updated sum of total weights.
    """
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
            sum_tw.value += hash_tw_of_trans[cJ]
    return result


def node_code_combination(a, b, sum_tw):
    """
    Combines two node codes and calculates the sum of their total weights.

    Args:
        a: The first node code.
        b: The second node code.
        sum_tw: A shared value to store the sum of total weights.

    Returns:
        The combined node code and the updated sum of total weights.
    """
    result = []
    for bJ in b:
        for aI in a:
            if bJ.pre_value < aI.pre_value and bJ.post_value > aI.post_value:
                if result and result[-1].pre_value == bJ.pre_value and result[-1].post_value == bJ.post_value:
                    result[-1].tw += aI.tw
                else:
                    temp = NodeTree()
                    temp.pre_value = bJ.pre_value
                    temp.post_value = bJ.post_value
                    temp.tw = aI.tw
                    result.append(temp)
                sum_tw.value += aI.tw
    return result


def item_union(a, b):
    """
    Performs the union of two items.

    Args:
        a: The first item.
        b: The second item.

    Returns:
        The union of the two items.
    """
    result = a[:]
    result.append(b[-1])
    return result


def read_trans_file(filename):
    """
    Reads the transaction file and returns the transaction weights database.

    Args:
        filename: The name of the transaction file.

    Returns:
        The transaction weights database.
    """
    trans_weights_DB = Transaction_Weights_DB()

    with open(filename, 'r') as file:
        lines = file.readlines()

        i = 0
        for line in lines:
            trans_weight = Transaction_Weight()
            trans_weight.trans_id = i + 1

            line_splitted = line.split(" ")

            for item_string in line_splitted:
                item = Item()
                try:
                    item.name = int(item_string)
                except:
                    continue
                trans_weight.items.append(item)
            trans_weights_DB.trans_weights.append(trans_weight)
            i += 1

    return trans_weights_DB


def read_weights_file(filename):
    """
    Reads the weights file and returns a dictionary of item weights.

    Args:
        filename: The name of the weights file.

    Returns:
        A dictionaryContinued:

    of item weights.
    """
    map_weights = {}
    with open(filename, 'r') as file:
        lines = file.readlines()

        item = 0
        for line in lines:
            map_weights[item + 1] = float(line)
            item += 1

    return map_weights


def write_output_of_file(fwis_top_rank_k, writer, count_FWIs):
    """
    Writes the output of the file.

    Args:
        fwis_top_rank_k: The top-k frequent weighted itemsets.
        writer: The file writer.
        count_FWIs: The count of frequent weighted itemsets.

    Returns:
        None.
    """
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
        values = f"|{i + 1:<10}|{item:<90}|{fwis_top_rank_k[i].ws:<20}|\n"
        writer.write(values)

        line = f"+{'-' * 10}+{'-' * 90}+{'-' * 20}+\n"
        writer.write(line)

    writer.close()


def print_stats(end_time, start_time, memory_used, type_tf):
    """
    Prints the statistics.

    Args:
        end_time: The end time.
        start_time: The start time.
        memory_used: The memory used.
        type_tf: The type of transaction file.

    Returns:
        None.
    """
    print("========== ", type_tf, "- STATUS ============")
    print(" Total time ~:", end_time - start_time, "ms")
    print(" Max memory:", memory_used / 1024 * 1024, "MB")
    print("==========================================")