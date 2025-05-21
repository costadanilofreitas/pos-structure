# encoding: utf-8
from old_helper import BaseRepository


class DeliveryOrderRepository(BaseRepository):
    
    def __init__(self, mb_context, pos_list):
        super(DeliveryOrderRepository, self).__init__(mb_context)
        self.pos_list = pos_list
        
    def get_order_json(self, order_id):
        def inner_func(conn):
            query = self._OrdersQuery.format(order_id)
            
            for x in conn.select(query):
                return x.get_entry("Value")
            
            return ''
        
        return self.execute_in_all_databases(inner_func, self.pos_list)
    
    _OrdersQuery = """
                    SELECT Value
                    FROM OrderCustomProperties
                    WHERE OrderId = '{}' AND (Key = 'REMOTE_ORDER_JSON' or Key = 'MANUAL_DELIVERY_ORDER_JSON')
                  """
