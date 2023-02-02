class Element:
    def __init__(self, tid, iutils, rutils):
        self.tid = tid
        self.iutils = iutils
        self.rutils = rutils


class UtilityList:
    def __init__(self):
        self.item = None
        self.elements = []
        self.sum_iutils = 0
        self.sum_rutils = 0

    def set_item(self, item):
        self.item = item

    def add_element(self, element):
        self.sum_iutils += element.iutils
        self.sum_rutils += element.rutils
        self.elements.append(element)

    def get_support(self):
        return len(self.elements)

    def to_str(self):
        print("item {}".format(self.item))
        for item in self.elements:
            print("tid {}  --  iutils {}  --  rutils {}".format(item.tid, item.iutils, item.rutils))

class Pair:
    def __init__(self):
        self.item = 0
        self.utility = 0
