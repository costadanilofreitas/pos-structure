import json

from deliveryreport.model import DeliveryOrder


class DeliveryReport(object):
    def __init__(self, order_repository, product_repository):
        self.order_repository = order_repository
        self.product_repository = product_repository
        
    def get_delivery_order(self, order_id):
        unfiltered_order_json = self.order_repository.get_order_json(order_id)
        order_json = [x for x in unfiltered_order_json if x][0]
        return DeliveryOrder(order_json)
    
    def get_products(self):
        return self.product_repository.get_products_name()
