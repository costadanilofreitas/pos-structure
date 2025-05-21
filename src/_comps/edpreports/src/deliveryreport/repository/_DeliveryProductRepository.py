# encoding: utf-8
from old_helper import BaseRepository


class DeliveryProductRepository(BaseRepository):
    
    def __init__(self, mb_context):
        super(DeliveryProductRepository, self).__init__(mb_context)
        
    def get_products_name(self):
        def inner_func(conn):
            products = {}
            query = self._ProductsQuery
            
            for x in conn.select(query):
                products[x.get_entry("ProductCode")] = x.get_entry("ProductName")
            
            return products
        
        return self.execute_with_connection(inner_func)
    
    _ProductsQuery = """
                    SELECT DISTINCT ProductCode, ProductName
                    FROM Product
                  """
