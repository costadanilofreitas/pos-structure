# -*- coding: utf-8 -*-

from _OrderDataFormatter import OrderDataFormatter
from repository import OrderRetrieverRepository


class OrderRetrieverService(object):
    def __init__(self, order_retriever_repository, order_data_formatter):
        # type: (OrderRetrieverRepository, OrderDataFormatter) -> None
        self.order_retriever_repository = order_retriever_repository
        self.order_data_formatter = order_data_formatter

    def get_orders_data(self, data):
        # type: (str) -> unicode
        data_list = data.split("\0")
        initial_order_id = int(data_list[0])
        last_order_id = None
        if len(data_list) > 1:
            last_order_id = int(data_list[1])

        order_data_list = self.order_retriever_repository.get_order_data_list(initial_order_id, last_order_id)
        return self.order_data_formatter.format_order_data_list(order_data_list)

    def get_last_order_id(self):
        return str(self.order_retriever_repository.get_last_order_id())
