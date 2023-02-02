from common import UtilityList, Element, Pair


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

    def run_algorithm(self, data_chess, tran_util, data_util):
        # Get TWU
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
        list_of_utility_lists.sort(reverse=False, key=sort_transaction)

        for tid, item in enumerate(data_chess, start=1):
            remaining_utility = 0
            revised_transaction = []
            for i in range(len(item)):
                pair = Pair()
                pair.item = item[i]
                pair.utility = data_util[tid-1][i]
                if self.map_item_to_TWU[pair.item] >= self.min_utility:
                    revised_transaction.append(pair)
                    remaining_utility += pair.utility

            revised_transaction.sort(reverse=True, key=sort_transaction)

            for pair in revised_transaction:
                remaining_utility = remaining_utility - pair.utility
                utility_list_of_item = map_item_to_utility_list[pair.item]
                element = Element(tid, pair.utility, remaining_utility)
                utility_list_of_item.add_element(element)

        # Mine the database recursively
        hui_result = []
        self.hui_miner(None, list_of_utility_lists, self.min_utility, hui_result)
        # for item in hui_result:
        #     item.to_str()
        return hui_result

    def hui_miner(self, pUL, ULs, min_utility, hui_result):
        for i in range(len(ULs)):
            X = ULs[i]
            # if pX is a high utility itemset.
            # we save the itemset: px
            if X.sum_iutils >= min_utility:
                # save to file
                hui_result.append(X)
            if (X.sum_iutils + X.sum_rutils) >= min_utility:
                exULs = []
                for j in range(i + 1, len(ULs)):
                    Y = ULs[j]
                    exULs.append(self.construct(pUL, X, Y))
                self.hui_miner(X, exULs, min_utility, hui_result)

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
