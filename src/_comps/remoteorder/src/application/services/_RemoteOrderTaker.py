# -*- coding: utf-8 -*-

import logging
import time
from typing import List
from threading import Lock
from xml.etree import cElementTree as eTree

import sysactions
from application.compositiontree import CompositionTree
from typing import List

from application.model import RemoteOrder, CurrentOrderItem
from application.repository import OrderRepository, ProductRepository
from application.services import OrderTakerWrapper, RemoteOrderItemCreator

logger = logging.getLogger("RemoteOrder")


class RemoteOrderTaker(object):
    def __init__(self, pos_id, order_taker_wrapper, order_item_creator, order_repository, product_repository,
                 delivery_fee_part_code):
        # type: (int, OrderTakerWrapper, RemoteOrderItemCreator, ProductRepository, OrderRepository, str) -> None
        self.pos_id = pos_id
        self.order_item_creator = order_item_creator
        self.order_taker_wrapper = order_taker_wrapper
        self.order_repository = order_repository

        self.delivery_fee_part_code = delivery_fee_part_code
        delivery_fee_exists = product_repository.product_code_exists(self.delivery_fee_part_code)
        
        self.order_taker_wrapper_lock = Lock()

    def save_remote_order(self, remote_order, order_trees):
        # type: (RemoteOrder, List[CompositionTree]) -> int
        with self.order_taker_wrapper_lock:
            order_id = self.order_taker_wrapper.create_order(self.pos_id, remote_order)

            self.order_item_creator.create_current_order_items(self.pos_id, order_id,
                                                               order_trees,
                                                               remote_order.pickup.type == "delivery")

            self._insert_delivery_fee_as_product(order_id, remote_order.delivery_fee, len(order_trees))

            self.order_taker_wrapper.add_comments(self.pos_id, order_id, order_trees)

            self.order_taker_wrapper.add_prep_time(self.pos_id, order_id)

            if remote_order.discount_amount:
                self.order_taker_wrapper.apply_discount(self.pos_id, remote_order.discount_amount)

            self.order_taker_wrapper.save_order(self.pos_id)

        return order_id

    def _insert_delivery_fee_as_product(self, order_id, delivery_fee, line_number):
        if delivery_fee:
            item = CurrentOrderItem()
            item.order_id = order_id
            item.line_number = line_number + 1
            item.item_id = "1"
            item.level = 0
            item.part_code = self.delivery_fee_part_code
            item.overwritten_unit_price = delivery_fee
            item.ordered_quantity = 1
            item.included_quantity = 0
            item.decremented_quantity = 0
            item.default_qty = 0
            item.discount_amount = 0
            item.surcharge_amount = 0
            item.only_flag = 0

            item_id = ".".join([item.item_id, item.part_code])
            self.order_taker_wrapper.create_item(self.pos_id, item_id, 1)
            self.order_repository.update_current_order_items(self.pos_id, [item])
            self.set_order_custom_property(order_id, "DELIVERY_FEE_PART_CODE", self.delivery_fee_part_code)
            self.set_order_custom_property(order_id, "DELIVERY_FEE_VALUE", delivery_fee)
    
    def check_business_period(self):
        retry = 0
        max_retry = 5
        while retry < max_retry:
            try:
                self.order_taker_wrapper.check_business_period(self.pos_id)
                break
            except BaseException as _:
                if retry < max_retry:
                    retry += 1
                    logger.exception("Error checking business period. Try#{}".format(retry))
                    continue

                logger.exception("Error checking business period and exceeded the max retry quantity")
                raise

    def save_order(self, order_id):
        model = sysactions.get_model(self.pos_id)
        order_taker = sysactions.get_posot(model)
        self.order_taker_wrapper.prepare_order_state(model, order_id, order_taker, self.pos_id)
        self.order_taker_wrapper.save_order(self.pos_id)
        return order_id

    def save_error_order(self, remote_order):
        order_id = self.get_local_order_id(remote_order)
        if order_id is None:
            order_id = self.order_taker_wrapper.essential_create_order(self.pos_id, remote_order)

            self._wait_model_update_with_current_order(order_id)
            
        self.order_taker_wrapper.save_order(self.pos_id)
        return order_id

    def _wait_model_update_with_current_order(self, order_id):
        time_limit = time.time() + 5.0
        while time.time() < time_limit:
            model = sysactions.get_model(self.pos_id)
            current_order_id = sysactions.get_current_order(model).get("orderId")
            if current_order_id == order_id:
                break
            time.sleep(0.1)

    def finalize_remote_order(self, remote_order):
        # type: (RemoteOrder) -> None
        with self.order_taker_wrapper_lock:
            order_id = remote_order.custom_properties["local_order_id"].value
            self.order_taker_wrapper.finalize_order(self.pos_id, order_id)

    def get_local_order_id(self, remote_order):
        # type: (RemoteOrder) -> int
        return self.order_repository.get_local_order_id(self.pos_id, remote_order.id)

    def get_local_order_id_from_original(self, remote_order):
        # type: (RemoteOrder) -> int
        return self.order_repository.get_local_order_id(self.pos_id, remote_order.originator_id)

    def get_local_order(self, local_order_id):
        # type: (int) -> eTree.XML
        return self.order_taker_wrapper.get_order_pict(self.pos_id, local_order_id)

    def get_order_tree(self, local_order_id, remote_order_id):
        # type: (int, int) -> eTree.XML
        return self.order_taker_wrapper.get_order_tree(self.pos_id, local_order_id, remote_order_id)

    def cancel_order(self, remote_order):
        # type: (RemoteOrder) -> None
        with self.order_taker_wrapper_lock:
            self.order_taker_wrapper.cancel_order(self.pos_id, remote_order.custom_properties["local_order_id"].value)

    def update_order(self, remote_order_id, local_order_id, order_trees):
        # type: (unicode, int, unicode) -> None
        with self.order_taker_wrapper_lock:
            self.order_taker_wrapper.update_order(self.pos_id, remote_order_id, local_order_id, order_trees)

    def set_order_custom_property(self, order_id, key, value):
        # type: (int, unicode, unicode) -> None
        self.order_taker_wrapper.set_order_custom_property(self.pos_id, order_id, key, value)
        
    def get_order_custom_property(self, key, order_id):
        # type: (int, unicode, unicode) -> None
        return self.order_taker_wrapper.get_order_custom_property(self.pos_id, order_id, key)
