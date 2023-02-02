def load_dataset_util(filename):
    with open(filename) as f:
        lines = f.readlines()

    data = []
    data_util = []
    sum_util = []
    item_list = []

    for line in lines:
        part = line.split(':')

        # Tách phần đầu
        items = part[0].split()
        tran = []
        for item in items:
            tran.append(int(item))
            if item not in item_list:
                item_list.append(item)
        data.append(tran)
        # Tách phần 2
        sum_util.append(int(part[1]))

        # Tách phần 3
        items = part[2].split()
        tran_util = []
        for item in items:
            tran_util.append(int(item))
        data_util.append(tran_util)

    # Kết quả:
    # data: list of list
    # sum_util: list
    # data_util: list of list
    # item_list: list
    return data, sum_util, data_util, sorted(item_list)