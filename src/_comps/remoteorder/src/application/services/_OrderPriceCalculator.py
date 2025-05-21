# -*- coding: utf-8 -*-

from application.compositiontree import CompositionTree
from application.services import PriceService
from typing import List


class OrderPriceCalculator(object):
    def __init__(self, price_service):
        # type: (PriceService) -> None
        self.price_service = price_service

    def calculate_order_price(self, order_trees, app=False):
        # type: (List[CompositionTree], bool) -> float
        order_price = 0

        for order_tree in order_trees:
            order_price += self._calculate_price(order_tree, u"1", app)

        return order_price

    def _calculate_price(self, order_tree, current_context, app):
        # type: (CompositionTree, unicode, bool) -> int
        total_price = 0

        price_lists = [u"EI", u"DL"] if app else None
        prices = self.price_service.get_best_price(current_context, order_tree.product.part_code, price_lists)
        if prices is not None:
            if order_tree.product.current_qty > 0:
                if prices[0] == 0 and order_tree.product.default_qty is not None:
                    product_qty = order_tree.product.current_qty - order_tree.product.default_qty
                else:
                    product_qty = order_tree.product.current_qty
                if product_qty > 0:
                    total_price += product_qty * prices[0] + product_qty * prices[1]

        for son in order_tree.sons:
            total_price += self._calculate_price(son, current_context + "." + str(order_tree.product.part_code), app)

        return total_price
