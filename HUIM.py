from common import UtilityList, Element, Pair

import sys
def sort_transaction(pair):
    return pair.item


class AlgoHUIMiner:
    def __init__(self, min_utility):
        self.start_timestamp = 0
        self.end_timestamp = 0
        self.hui_count = 0
        self.map_item_to_TWU = {}
        self.join_count = 0
        self.min_utility = min_utility
        self.EUCS = {}
        self.itemset_buffer = []
        self.itemset_buffer_size = 200
        self.hui_result = []

    def run_algorithm(self, data_chess, tran_util, data_util):
        # Get TWU

        self.itemset_buffer = [0] * self.itemset_buffer_size

        for i, row in enumerate(data_chess):
            transaction_utility = tran_util[i]
            for j, item in enumerate(row):
                try:
                    twu = self.map_item_to_TWU[item]
                except:
                    twu = None
                if twu is None:
                    twu = transaction_utility
                else:
                    twu = twu + transaction_utility
                self.map_item_to_TWU.update({item: twu})

        list_of_utility_lists = []
        map_item_to_utility_list = {}

        # For each item
        for item in self.map_item_to_TWU.keys():
            if self.map_item_to_TWU[item] > self.min_utility:
                uList = UtilityList()
                uList.set_item([item])
                map_item_to_utility_list.update({item: uList})
                list_of_utility_lists.append(uList)

        # SORT THE LIST OF HIGH TWU ITEMS IN ASCENDING ORDER
        list_of_utility_lists.sort(key=lambda ul: self.map_item_to_TWU[ul.item[0]])

        for tid, item in enumerate(data_chess, start=1):
            remaining_utility = 0
            transac_util = tran_util[tid - 1]
            revised_transaction = []
            for i in range(len(item)):
                pair = Pair()
                pair.item = item[i]
                pair.utility = data_util[tid-1][i]
                if self.map_item_to_TWU[pair.item] >= self.min_utility:
                    revised_transaction.append(pair)
                    remaining_utility += pair.utility

            revised_transaction.sort(key=lambda p: self.map_item_to_TWU[p.item])

            for i in range(len(revised_transaction)):
                pair = revised_transaction[i]
                remaining_utility = remaining_utility - pair.utility
                utility_list_of_item = map_item_to_utility_list[pair.item]
                element = Element(tid, pair.utility, remaining_utility)
                utility_list_of_item.add_element(element)
                # populate EUCS
                for j in range(i + 1, len(revised_transaction)):
                    item = revised_transaction[i].item
                    next_item = revised_transaction[j].item
                    if item in self.EUCS:
                        if next_item in self.EUCS[item]:
                            self.EUCS[item][next_item] += transac_util
                        else:
                            self.EUCS[item][next_item] = transac_util
                    else:
                        self.EUCS[item] = {next_item: transac_util}

        # Mine the database recursively
        self.hui_miner(None, list_of_utility_lists,  0)
        # print(self.hui_result)
        return self.hui_result

    def hui_miner(self, pUL, ULs,  prefix_len):
        for i in range(len(ULs)):
            X = ULs[i]
            # if pX is a high utility itemset.
            # we save the itemset: px
            # print(X.sum_iutils)
            if X.sum_iutils >= self.min_utility:
                # save to file
                print(X.item)
                self.hui_result.append(X)
                # self.output(prefix_len, X.item, X.sum_iutils)
            if X.sum_iutils + X.sum_rutils >= self.min_utility:
                exULs = []
                for j in range(i + 1, len(ULs)):
                    Y = ULs[j]
                    # if X.item in self.EUCS and Y.item in self.EUCS[X.item]:
                    #     if self.EUCS[X.item][Y.item] >= self.min_utility:
                    exULs.append(self.construct(pUL, X, Y))
                try:
                    self.itemset_buffer[prefix_len] = X.item
                except IndexError:
                    sys.exit(
                        f"Error: itemset_buffer_size ({self.itemset_buffer_size}) is too small"
                    )
                self.hui_miner(X, exULs, prefix_len + 1)

    def output(self, prefix_len: int, item: int, util: int) -> None:
        """
        Write the given high utility itemset and it's utility to self.output_file.

        Parameters:
            prefix_len: length of the prefix itemset
            item: item extension of the prefix itemset
            util: utility of the itemset
        """
        self.hui_count += 1
        line = []
        for i in range(prefix_len):
            line.append(self.itemset_buffer[i])
        line.append(item)
        u = UtilityList()
        u.set_item(line)
        u.sum_iutils = util
        self.hui_result.append(u)

    def construct(self, P, px, py):
        pxyUL = UtilityList()
        arrLable = list(px.item) + list(py.item)
        s = set(arrLable)
        unique_l = list(s)
        pxyUL.set_item(unique_l)
        for ex in px.elements:
            ey = self.find_element_with_TID(py, ex.tid)
            if ey is None:
                continue
            if P is None:
                eXY = Element(ex.tid, ex.iutils + ey.iutils, ey.rutils)
                pxyUL.add_element(eXY)
            else:
                e = self.find_element_with_TID(P, ex.tid)
                if e is not None:
                    eXY = Element(ex.tid, ex.iutils + ey.iutils - e.iutils, ey.rutils)
                    pxyUL.add_element(eXY)
        return pxyUL

    @staticmethod
    def find_element_with_TID(ulist, tid):
        list = ulist.elements
        first = 0
        last = len(list) - 1

        while first <= last:
            middle = (first + last) // 2
            if list[middle].tid < tid:
                first = middle + 1
            else:
                if list[middle].tid > tid:
                    last = middle - 1
                else:
                    return list[middle]
        return None
