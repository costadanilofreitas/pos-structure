# -*- coding: utf-8 -*-
from application.customexception import StoreClosedException
from application.model import ProcessedOrder, RemoteOrder
from application.services import ProcessedOrderBuilder, RemoteOrderParser, RemoteOrderTaker, RemoteOrderValidator, \
    StoreService
from typing import List


class RemoteOrderProcessor(object):
    def __init__(self, remote_order_parser, remote_order_validator, remote_order_taker, store_service, processed_order_builder, cancel_order_on_partner):
        # type: (RemoteOrderParser, RemoteOrderValidator, RemoteOrderTaker, StoreService, ProcessedOrderBuilder, bool) -> None
        self.remote_order_parser = remote_order_parser
        self.remote_order_validator = remote_order_validator
        self.remote_order_taker = remote_order_taker
        self.store_service = store_service
        self.processed_order_builder = processed_order_builder
        self.cancel_order_on_partner = cancel_order_on_partner

    def process_order(self, unavailable_items, remote_order):
        # type: (unicode, List[unicode]) -> (int, ProcessedOrder)
        
        order_id = self.remote_order_taker.get_local_order_id(remote_order)
        if order_id is None:
            order_trees, validation_ex = self.remote_order_validator.validate_order(remote_order, unavailable_items)
            order_id = self.remote_order_taker.save_remote_order(remote_order, order_trees)
            self.remote_order_validator.validate_order_price(remote_order, order_trees)
            
            if validation_ex:
                raise validation_ex
        else:
            order_trees = None
        processed_order = self.processed_order_builder.build_processed_order(remote_order.id, order_id, order_trees)

        return remote_order.id, processed_order
    
    def get_processed_order(self, remote_order_id, order_id):
        return self.processed_order_builder.build_processed_order(remote_order_id, order_id, None)

    def check_if_order_exists(self, confirmed_json):
        remote_order = RemoteOrder()
        remote_order.id = confirmed_json["reference"]
    
        if self.get_local_order_id(remote_order):
            return True
        return False
    
    def get_local_order_id(self, remote_order):
        return self.remote_order_taker.get_local_order_id(remote_order)

    def parse_order(self, remote_order_json, minimum=False):
        if minimum:
            return self.remote_order_parser.minimum_parse(remote_order_json)
    
        return self.remote_order_parser.parse_order(remote_order_json)
    
    def save_order(self, order_id):
        return self.remote_order_taker.save_order(order_id)
    
    def save_error_order(self, parsed_order):
        return self.remote_order_taker.save_error_order(parsed_order)
    
    def check_business_period(self):
        self.remote_order_taker.check_business_period()
