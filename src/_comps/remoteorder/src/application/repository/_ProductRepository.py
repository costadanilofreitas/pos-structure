# -*- coding: utf-8 -*-

from msgbus import MBEasyContext
from mwhelper import BaseRepository
from persistence import Connection
from typing import Dict


class ProductRepository(BaseRepository):
    def __init__(self, mb_context):
        # type: (MBEasyContext) -> None
        super(ProductRepository, self).__init__(mb_context)
        self.cached_get_all_products = None
        self.cached_get_all_product_types = None
        self.cached_get_tender_types = None
        
        self.get_all_products()

    def get_all_products(self):
        # type: () -> Dict[int, unicode]
        def inner_func(conn):
            # type: (Connection) -> Dict[int, unicode]
            return {int(x.get_entry(0)): str(x.get_entry(1)).decode("utf-8")
                    for x in conn.select("select ProductCode, ProductName from Product")}

        if not self.cached_get_all_products:
            self.cached_get_all_products = self.execute_with_connection(inner_func)

        return self.cached_get_all_products

    def get_all_product_types(self):
        # type: () -> Dict[int, int]
        def inner_func(conn):
            # type: (Connection) -> Dict[int, int]
            return {int(x.get_entry(0)): int(x.get_entry(1))
                    for x in conn.select("select ProductCode, ProductType from ProductKernelParams")}

        if not self.cached_get_all_product_types:
            self.cached_get_all_product_types = self.execute_with_connection(inner_func)

        return self.cached_get_all_product_types

    def get_tender_types(self):
        # type: () -> Dict[str, int]
        def inner_func(conn):
            # type: (Connection) -> Dict[str, int]
            return {str(x.get_entry(0)).lower(): int(x.get_entry(1))
                    for x in conn.select("select TenderDescr, TenderId from TenderType")}

        if not self.cached_get_tender_types:
            self.cached_get_tender_types = self.execute_with_connection(inner_func)

        return self.cached_get_tender_types
    
    def product_code_exists(self, product_code):
        product_exists = self.cached_get_all_products.get(int(product_code))
        if product_exists:
            return True
        
        return False
