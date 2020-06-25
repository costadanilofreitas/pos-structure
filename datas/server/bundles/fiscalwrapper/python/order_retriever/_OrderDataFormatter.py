from typing import List
from model import OrderData


class OrderDataFormatter(object):
    def __init__(self):
        pass

    def format_order_data(self, order_data):
        # type: (OrderData) -> unicode
        return str(order_data.order_id) + "\0" + \
               str(order_data.pos_id) + "\0" + \
               order_data.order_picture + "\0" + \
               order_data.order_xml

    def format_order_data_list(self, order_data_list):
        # type: (List[OrderData]) -> unicode
        ret = ""
        for order_data in order_data_list:
            ret += self.format_order_data(order_data) + "\0"

        return ret[0:-1]
