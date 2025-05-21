# -*- coding: utf-8 -*-

from application.compositiontree import DbProductRepository
from application.mwmodel import MwOrderItem
from application.repository import OrderRepository, ApiOrderRepository, ProductRepository
from typing import List


class DefaultQuantityFixer(object):
    def __init__(self, order_repository, api_order_repository, db_product_repository, product_repository):
        # type: (OrderRepository, ApiOrderRepository, DbProductRepository, ProductRepository) -> None
        self.order_repository = order_repository
        self.api_order_repository = api_order_repository
        self.db_product_repository = db_product_repository

        self.all_product_types = product_repository.get_all_product_types()
        self.default_products = self.db_product_repository.get_default_products()

    def fix_default_quantity(self, pos_id, order_id):
        # Arrumar o default quantity que se perde ao sair do CurrentOrderItem
        mw_order = self.api_order_repository.get_order(order_id)
        items_to_update_default_quantity = []
        for order_item in mw_order.order_items:
            self._fix_item_default_quantity(order_item, items_to_update_default_quantity)

        self.order_repository.update_default_quantities(pos_id, order_id, items_to_update_default_quantity)

    def _fix_item_default_quantity(self, item, items_to_update):
        # type: (MwOrderItem, List[MwOrderItem]) -> None
        if item.parent is not None and item.parent.parent is not None and self.all_product_types[item.parent.part_code] == 1 and self.all_product_types[item.parent.parent.part_code] == 0:
            # Estamos em um item que o pai é um Option e o avô é um Product -> Estamos em um ingrediente
            key = (str(item.parent.parent.part_code), str(item.parent.part_code))
            if key in self.default_products and str(item.part_code) in self.default_products[key]:
                item.default_qty = 1
                items_to_update.append(item)

        if item.sons is not None:
            for son in item.sons:
                self._fix_item_default_quantity(son, items_to_update)
