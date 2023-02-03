from readData import load_dataset_util
import numpy as np
from pulp import LpMinimize, LpProblem, LpVariable, LpAffineExpression, PULP_CBC_CMD
from HUI import AlgoHUIMiner
from datetime import datetime
import time


class PPUM_ILP:
    def __init__(self, HUI, min_utility, data_chess, item_list, sum_util, data_util, Is):
        """
            HUI: HUIMiner
            M: min_util
            Is:
            NHI_TB:
            SHI_TB:
        """
        self.min_utility = min_utility
        self.D_ = []
        self.Is = Is
        # self.Is = [[1, 2], [1, 3], [1, 4]]
        self.HUI = HUI
        self.data_chess = data_chess
        self.item_list = item_list
        self.sum_util = sum_util
        self.data_util = data_util

    @staticmethod
    def compare_array(array_one, array_two):
        """
            compare 2 arrays return bool
        """
        if len(array_one) == len(array_two):
            count = 0
            for i in array_one:
                for j in array_two:
                    if i == j:
                        count = count + 1
            if count == len(array_one):
                return True
            else:
                return False
        else:
            return False

    def filter_NHI_and_SHI_to_HUI(self):
        """
            HUI -> SHI_TB and NHI_TB
        """
        NHI_TB = []
        SHI_TB = []
        for hui_item in self.HUI:
            lable = hui_item.item
            isIs = False
            for item_Is in self.Is:
                if self.compare_array(lable, item_Is):
                    SHI_TB.append(hui_item)
                    isIs = True
            if not isIs:
                if len(NHI_TB) == 0:
                    NHI_TB.append(hui_item)
                else:
                    # lọc NHI table ra
                    # for nhi_item in self.NHI_TB:
                    NHI_TB.append(hui_item)
        return NHI_TB, SHI_TB

    def get_tid(self, elements):
        result = []
        for element in elements:
            result.append(element.tid)
        return result

    def get_tid_with_item(self, nhi_table, item):
        for i in nhi_table:
            if len(np.intersect1d(item, i.item)) == len(item):
                return self.get_tid(i.elements)
        return None

    def arr_sum(self, item):
        """

        """
        arr_sum = {}
        for X in item:
            dict_aa = {}
            dict_aa[X] = LpAffineExpression()
            arr_sum.update(dict_aa)
        return arr_sum

    def index_TIDs(self, i):
        for item in self.HUI:
            if item.item == i:
                arr = []
                for row in item.elements:
                    arr.append(row.tid)
                return arr
                break

    def arr_Si(self, arr, temp, deci_variables):
        """
            {'A': 1*A1 + 1*A5 + 1*A7 + 0, 'B': 1*B1 + 1*B5 + 1*B7 + 0}
            {'A': 1*A2 + 1*A8 + 1*A9 + 0, 'C': 1*C2 + 1*C8 + 1*C9 + 0}
            {'A': 1*A1 + 1*A5 + 1*A8 + 0, 'D': 1*D1 + 1*D5 + 1*D8 + 0}
        """
        for item_vb in deci_variables:
            for item in arr:
                if (item == item_vb):
                    for i in self.Is:
                        if temp == i:
                            for j in self.index_TIDs(i):
                                arr[item] += deci_variables[item][j]
        return arr

    def check_nhi_in_shi(self, item):
        """
            kiểm tra Nhi có trong Shi hay không
        """
        strItem = []
        for a in self.Is:
            for i in a:
                for j in item:
                    if j not in strItem and (i == j):
                        strItem.append(j)
        return strItem

    def right_side(self, item, arr, X):
        """
            Tính vế phải
        """
        sum_ = 0
        for x in arr:
            for i, j in enumerate(self.HUI):
                if j.item == X:
                    for k in j.elements:
                        if k.tid == x:
                            sum_ += k.iutils
                    break
        return item.sum_iutils - sum_

    def arr_X(self, TIDs, item):
        arr = []
        for X in self.Is:
            for i in self.index_TIDs(X):
                for j in range(len(TIDs[item])):
                    if i == j and TIDs[item][j] != 0:
                        arr.append(i + 1)
        return arr
    @staticmethod
    def my_print(u):
        for item in u:
            item.to_str()

    @staticmethod
    def get_external_utility():
        external_utility = {}
        for item in item_list:
            array_util = []
            for i in range(len(data_chess)):

                try:
                    index = data_chess[i].index(int(item))
                except:
                    index = -1
                if index >= 0:
                    array_util.append(data_util[i][index])
            gcd = np.gcd.reduce(array_util)  # Ước chung lớn nhất
            temp = {int(item): gcd}
            external_utility.update(temp)
        return external_utility

    def algorithm(self):
        """
            The PPUM-ILP algorithm
        """
        # Table constructions:
        NHI_TB, SHI_TB = self.filter_NHI_and_SHI_to_HUI()

        # Preprocessing:
        NHI_TB_Temp = NHI_TB.copy()
        NHI_TB = []
        for ni in NHI_TB_Temp:
            a = np.array(ni.item)
            c = np.array(self.get_tid(ni.elements))

            for si in SHI_TB:
                b = np.array(si.item)
                d = np.array(self.get_tid(si.elements))
                inter = np.intersect1d(a, b)
                inter2 = np.intersect1d(c, d)
                inter3 = np.setdiff1d(a, b)

                if len(inter) > 0 and len(inter2) > 0:
                    if len(inter3) == 0 and np.array_equal(c, d):
                        break
                    else:
                        NHI_TB.append(ni)
                        break

        NHI_TB_Temp = NHI_TB.copy()
        NHI_TB = []
        for ni in NHI_TB_Temp:
            c = np.array(self.get_tid(ni.elements))
            isDelete = False
            for nj in NHI_TB_Temp:
                inter3 = np.setdiff1d(nj.item, ni.item)
                d = np.array(self.get_tid(nj.elements))
                if not np.array_equal(ni.item, nj.item) and len(inter3) == 0 and np.array_equal(c, d):
                    isDelete = True
                    break
            if not isDelete:
                NHI_TB.append(ni)
        """
            CSP formulation:
            Biến quyết định x, y, z
        """
        deci_variables = {}
        for item_is in self.Is:
            for X in item_is:
                temp = {X: {i: LpVariable(name=f"{X}_{i}", lowBound=1) for i in range(1, len(self.data_chess) + 1)}}
                deci_variables.update(temp)
        """
            Khởi tạo model:
            model : Lable : 5 * A1 + 5 * A5 + 5 * A7 + 3 * B1 <= min_utility
        """
        model = LpProblem(name="resource-allocation-ILP", sense=LpMinimize)

        """
            model SHI_TB:
            AB ∶ 5(u11 + u51 + u71) + 3(u12 + u52 + u72) < 80
        """
        external_utility = self.get_external_utility()

        sum_AB = 0
        for item_is in self.Is:
            sum = 0
            result = self.arr_Si(self.arr_sum(item_is), item_is, deci_variables)
            for item_lable in result:
                sum += external_utility[item_lable] * result[item_lable]
                sum_AB += result[item_lable]
            model += (sum <= self.min_utility - 1, item_is)
        """
            model NHI_TB:
            A ∶ 5(u11 + u51 + u71) ≥ 80 − 70,
            AD ∶ 5(u11 + u51) ≥ 80 − 75,
            BD ∶ 3(u12 + u52) ≥ 80 − 42,
            ABDE ∶ 5u11 + 3u12 ≥ 80 − 34
            
            VP:
                get tid của  A or B or AB
                get tid item, 
                lấy tid chung
                
                tổng - sum(tid chung của A or B or AB)
        """
        for item in NHI_TB:
            X = self.check_nhi_in_shi(item.item)
            tid = self.get_tid(item.elements)
            tid2 = self.get_tid_with_item(SHI_TB, X)
            # so sáng tid và tid2 lấy trùng nhau == arr
            if tid2 is not None:
                arr = np.intersect1d(tid, tid2)
                sum_item = 0
                for i in X:
                    x = external_utility[i]
                    sum_item_2 = 0
                    for j in arr:
                        for k in deci_variables:
                            if k == i:
                                sum_item_2 += deci_variables[k][j]
                    sum_item += x * sum_item_2
                model += (sum_item >= self.min_utility - self.right_side(item, arr, X), item.item)

        # model tổng
        sum_temp = 0
        for i in sum_AB:
            sum_temp += i
        model += sum_temp

        # Solve the optimization problem
        model.solve( PULP_CBC_CMD(msg=False))
        dict_variables = {}
        for var in model.variables():
            new_dict = {}
            new_dict[var.name] = round(var.value())
            dict_variables.update(new_dict)

        # Get transactional database
        db = []
        for index_row, items in enumerate(self.data_util):
            row = []
            for i in external_utility:
                result = 0
                for index_item, item in enumerate(items):
                    if self.data_chess[index_row][index_item] == i:
                        result = int(item / external_utility[self.data_chess[index_row][index_item]])
                        break
                row.append(result)
            db.append(row)
        now = datetime.now()
        file_name = "output/transactional-database-{}.csv"
        np.savetxt(file_name.format(now.strftime("%d%m%Y")), db, fmt='%d', delimiter=",")

        print("Tính toán xong, đang cập nhật lại dữ liệu.")
        # Get Perturbed database
        for item in dict_variables:
            lable = int(item.split("_")[0])
            tid = int(item.split("_")[1])
            value = dict_variables[item]
            db[tid-1][lable-1] = value

        # convert to date String
        file_name = "output/perturbed-database-{}.csv"
        np.savetxt(file_name.format(now.strftime("%d%m%Y")), db, fmt='%d', delimiter=",")
        print("Done!")
    def run(self):
        self.algorithm()


if __name__ == "__main__":
    delta = 0.28
    file_name = 'input/chess_test.txt'
    start = time.time()
    print("\nĐang đọc file test.txt")
    data_chess, sum_util, data_util, item_list = load_dataset_util(file_name)
    min_utility = sum(sum_util) * delta
    print("Đọc file xong. \nKhai thác hui với min utility bằng", min_utility)

    hui_miner = AlgoHUIMiner(min_utility)
    hui = hui_miner.run_algorithm(data_chess, sum_util, data_util)
    print('Khai thác xong với tổng thời gian khai thác HUI (HUI Miner): %s giây' % (time.time() - start))
    print("\n-----------------\n")
    start2 = time.time()
    Is = [[1, 2]]
    print("Sử dụng thuật toán PPUM_ILP để ẩn tập nhạy cảm: ", Is)
    PPUM_ILP(hui, min_utility, data_chess, item_list, sum_util, data_util, Is).run()

    print('Tổng thời gian: %s giây' % (time.time() - start2))

