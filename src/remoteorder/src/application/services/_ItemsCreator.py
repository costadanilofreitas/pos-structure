# -*- coding: utf-8 -*-

from application.apimodel import Item, ProductType
from application.compositiontree import DbProductRepository
from application.mwmodel import MwOrderItem
from application.repository import ProductRepository
from memorycache import CacheManager, PeriodBasedExpiration
from typing import List


class ItemsCreator(object):
    def __init__(self, product_repository, db_product_repository):
        # type: (ProductRepository, DbProductRepository) -> None
        self.product_repository = product_repository
        self.db_product_repository = db_product_repository
        self.product_name_cache = CacheManager(PeriodBasedExpiration(5), new_object_func=self._renew_product_name_cache)
        self.product_type_cache = CacheManager(PeriodBasedExpiration(5), new_object_func=self._renew_product_type_cache)
        self.default_products = CacheManager(PeriodBasedExpiration(5), new_object_func=self._renew_default_products_cache)

    def create_items(self, order_items):
        # type: (List[MwOrderItem]) -> List[Item]
        ret = []
        for item in order_items:
            ret.append(self._convert_item(item))

        return ret

    def _get_product_name(self, part_code):
        # type: (int) -> unicode
        return (self.product_name_cache.get_cached_object() or {}).get(part_code)

    def _get_product_type(self, part_code):
        # type: (int) -> int
        if part_code in self.product_type_cache.get_cached_object():
            return self.product_type_cache.get_cached_object()[part_code]
        
        return None

    def _get_default_quantity(self, product_father, option_father, part_code):
        default_product_dict = self.default_products.get_cached_object()
        key = (str(product_father).decode("utf-8"), str(option_father).decode("utf-8"))
        if key in default_product_dict:
            products_dict = default_product_dict[key]
            if str(part_code).decode("utf-8") in products_dict:
                return 1
            else:
                return 0
        else:
            return 0

    def _renew_product_name_cache(self):
        return self.product_repository.get_all_products()

    def _renew_product_type_cache(self):
        return self.product_repository.get_all_product_types()

    def _renew_default_products_cache(self):
        return self.db_product_repository.get_default_products()

    def _convert_item(self, mw_order_item):
        # type: (MwOrderItem) -> Item
        new_item = Item()
        new_item.part_code = mw_order_item.part_code
        new_item.context = mw_order_item.context
        new_item.product_name = self._get_product_name(mw_order_item.part_code)
        new_item.quantity = mw_order_item.quantity if mw_order_item.quantity is not None else 0
        if mw_order_item.parent is not None and self._get_product_type(mw_order_item.parent.part_code) == 1 \
                and mw_order_item.parent.parent is not None and self._get_product_type(mw_order_item.parent.parent.part_code) == 0:
            new_item.default_quantity = self._get_default_quantity(mw_order_item.parent.parent.part_code, mw_order_item.parent.part_code, mw_order_item.part_code)
        else:
            new_item.default_quantity = 0
        product_type = self._get_product_type(mw_order_item.part_code)
        if product_type == 0:
            new_item.product_type = ProductType.PRODUCT
        elif product_type == 1:
            new_item.product_type = ProductType.OPTION
        else:
            new_item.product_type = ProductType.COMBO

        for son in mw_order_item.sons:
            new_item.sons.append(self._convert_item(son))

        return new_item
