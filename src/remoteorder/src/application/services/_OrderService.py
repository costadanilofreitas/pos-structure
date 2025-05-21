# -*- coding: utf-8 -*-

import json
import logging
import sys
import time
import six

from datetime import datetime, timedelta
from typing import List, Union, Optional
from xml.etree import cElementTree as eTree

from application.apimodel import Order, OrderStatus
from application.customexception import InvalidJsonException, OrderNotFoundException, ValidationError, OrderException, \
    ValidationException, PaymentException, LogisticException
from application.model import RemoteOrder, CustomProperty
from application.mwmodel import MwOrder, MwOrderStatus
from application.repository import ApiOrderRepository, CanceledOrderRepository, ProducedOrderRepository
from application.services import ItemsCreator, RemoteOrderTaker

logger = logging.getLogger("RemoteOrder")


class OrderService(object):
    def __init__(self, order_repository, items_creator, remote_order_taker, canceled_order_repository,
                 produced_order_repository):
        # type: (ApiOrderRepository, ItemsCreator, RemoteOrderTaker, CanceledOrderRepository, ProducedOrderRepository) -> None # noqa
        self.order_repository = order_repository
        self.items_creator = items_creator
        self.remote_order_taker = remote_order_taker
        self.canceled_order_repository = canceled_order_repository
        self.produced_order_repository = produced_order_repository

    def get_order(self, order_id):
        # type: (int) -> Union[Order, None]
        mw_order = self.order_repository.get_order(order_id)

        if mw_order is None:
            return None

        orders = self._convert_mworder_to_order([mw_order])
        return orders[0]

    def get_order_id(self, remote_order_id):
        # type: (str) -> int
        mw_order = self.order_repository.get_order_by_remote_id(remote_order_id)
        if mw_order:
            return mw_order.id
        else:
            error_msg = "The order was not found in the database. RemoteOrderId: {}".format(remote_order_id)
            raise OrderNotFoundException(remote_order_id, error_msg)
        
    def get_stored_orders(self, return_paid_orders):
        # type: (bool) -> List[Order]
        
        all_mw_orders = self.order_repository.get_stored_orders(return_paid_orders)
        all_orders = self._convert_mworder_to_order(all_mw_orders)

        return all_orders

    def get_error_orders(self):
        # type: () -> List[Order]
        
        all_mw_orders = self.order_repository.get_error_orders()
        all_orders = self._convert_mworder_to_order(all_mw_orders)

        return all_orders

    def get_confirmed_orders(self):
        # type: () -> List[Order]
        
        all_mw_orders = self.order_repository.get_confirmed_orders()
        all_orders = self._convert_mworder_to_order(all_mw_orders)

        return all_orders

    def reprint_delivery_order(self, order_id):
        self.order_repository.reprint_delivery_order(order_id)

    @staticmethod
    def get_remote_order_id(data):
        try:
            parsed_json = json.loads(data, encoding="utf-8")  # type: dict
        except ValueError as ex:
            exception = InvalidJsonException(ex.message, data)
            raise six.reraise(InvalidJsonException, exception, sys.exc_info()[2])

        if "id" not in parsed_json:
            exception = InvalidJsonException("Json without 'id' tag", data)
            raise six.reraise(InvalidJsonException, exception, sys.exc_info()[2])
        return parsed_json["id"]

    def cancel_order(self, remote_order_id):
        mw_order = self.order_repository.get_order_by_remote_id(remote_order_id)
        if mw_order is None:
            error_msg = "The order was not found in the database. RemoteOrderId: {}".format(remote_order_id)
            logger.info(error_msg)
            raise OrderNotFoundException(remote_order_id, error_msg)

        if mw_order.status == MwOrderStatus.RECALLED:
            try:
                order_picture = self.remote_order_taker.get_local_order(mw_order.id)
                order_picture = order_picture.find("Order") if order_picture.find("Order") else order_picture
                mw_order.status = int(order_picture.get("stateId"))
                info_msg = "Order RECALLED - OrderStatus: {1}; RemoteOrderId: {0}"
                logger.info(info_msg.format(remote_order_id, mw_order.status))
            except Exception as _: # noqa
                mw_order.status = MwOrderStatus.VOIDED
                error_msg = "Order RECALLED - ERROR in Order Picture - VOIDING. RemoteOrderId: {}"
                logger.exception(error_msg.format(remote_order_id))

        if mw_order.status == MwOrderStatus.VOIDED:
            logger.info("The order is already VOIDED. RemoteOrderId: {}".format(remote_order_id))
            return True

        remote_order = RemoteOrder()
        custom_property = CustomProperty()
        custom_property.key = "local_order_id"
        custom_property.value = mw_order.id
        remote_order.custom_properties[custom_property.key] = custom_property

        self.remote_order_taker.cancel_order(remote_order)
        logger.info("The order has been VOIDED. RemoteOrderId: {}".format(remote_order_id))
        return True

    def send_order_to_production(self, order_id):
        # type: (str) -> None
        
        if self.order_repository.is_order_produced(order_id=order_id):
            logger.info("The order is already produced: #{}".format(order_id))
            return
        
        if not self.order_repository.order_exists(order_id):
            error_message = "The order with OrderId#{} was not found".format(order_id)
            raise ValidationException(ValidationError.OrderNotFound, error_message)

        _, remote_order_id, partner = self.order_repository.get_remote_order_info(order_id)

        remote_order = RemoteOrder()
        custom_property = CustomProperty()
        custom_property.key = "local_order_id"
        custom_property.value = order_id
        remote_order.custom_properties[custom_property.key] = custom_property

        original_exception = None
        try_qty = 0
        max_retry_qty = 3
        while try_qty < max_retry_qty:
            try_qty += 1
            try:
                message = "Trying to produce order. Try: {}/{}; Partner: {}; OrderId: {}; RemoteOrderId: {}"
                logger.info(message.format(try_qty, max_retry_qty, partner, order_id, remote_order_id))
                
                self.remote_order_taker.finalize_remote_order(remote_order)
                self.produced_order_repository.add_produced_order(order_id)
                
                if self.remote_order_taker.get_order_custom_property_value("DELIVERY_ERROR_TYPE", order_id):
                    self.set_order_custom_property(order_id, "DELIVERY_ERROR_TYPE", "clear")
                    self.set_order_custom_property(order_id, "DELIVERY_ERROR_DESCRIPTION", "clear")
                    self.set_order_custom_property(order_id, "DELIVERY_ORDER_MANUAL_CONFIRMED", "true")

                message = "Order successfully produced. Partner: {}; OrderId: {}; RemoteOrderId: {}"
                logger.info(message.format(partner, order_id, remote_order_id))
                break
            except (OrderException, PaymentException, Exception) as e:
                if not original_exception:
                    original_exception = e
                    
                if try_qty < max_retry_qty:
                    logger.exception("Error producing order. Try: {}/{}".format(try_qty, max_retry_qty))
                    time.sleep(1)
                    continue

                raise original_exception

    def confirm_produced_order(self, data):
        store_status_json = json.loads(data, encoding="utf-8")
        if "id" not in store_status_json:
            raise Exception("Data without id tag")

        remote_order_id = store_status_json["id"]

        self.produced_order_repository.mark_order_as_sent(remote_order_id=remote_order_id)

        logger.info("Order successfully produced: {}".format(remote_order_id))

    def _convert_mworder_to_order(self, mw_order_list, ignore_items=False):
        # type: (List[MwOrder], Optional[bool]) -> List[Order]
        all_orders = []
        for mw_order in mw_order_list:
            order = Order()
            order.id = mw_order.id
            order.total = mw_order.total
            order.order_status = mw_order.status
            order.business_period = mw_order.business_period

            for obj in mw_order.custom_properties:
                order.custom_properties[obj] = mw_order.custom_properties[obj].value

            if u"REMOTE_ORDER_ID" in mw_order.custom_properties:
                order.remote_id = mw_order.custom_properties[u"REMOTE_ORDER_ID"].value

            if u"CREATED_AT" in mw_order.custom_properties:
                order.receive_time = datetime.strptime(mw_order.custom_properties[u"CREATED_AT"].value, u"%Y-%m-%d %H:%M:%S")

            if u"CUSTOMER_NAME" in mw_order.custom_properties:
                order.customer_name = mw_order.custom_properties[u"CUSTOMER_NAME"].value

            if u"DELIVERYMAN" in mw_order.custom_properties:
                order.deliveryman = mw_order.custom_properties[u"DELIVERYMAN"].value

            if u"DELIVERYMAN_DATETIME" in mw_order.custom_properties:
                order.deliveryman_date_time = mw_order.custom_properties[u"DELIVERYMAN_DATETIME"].value

            if u"CONFIRM_DELIVERY_PAYMENT" in mw_order.custom_properties:
                order.confirm_delivery_payment = mw_order.custom_properties[u"CONFIRM_DELIVERY_PAYMENT"].value
                order.confirm_delivery_payment_datetime = mw_order.custom_properties[u"CONFIRM_DELIVERY_PAYMENT_DATETIME"].value

            if u"DELIVERY_ERROR_TYPE" in mw_order.custom_properties:
                delivery_error_type = mw_order.custom_properties[u"DELIVERY_ERROR_TYPE"].value
                order.delivery_error_type = delivery_error_type

            if u"DELIVERY_ERROR_DESCRIPTION" in mw_order.custom_properties:
                delivery_error_description = mw_order.custom_properties[u"DELIVERY_ERROR_DESCRIPTION"].value
                order.delivery_error_description = delivery_error_description

            order.status = OrderStatus.Ok

            if u"PICKUP_TIME" in mw_order.custom_properties:
                order.pickup_time = datetime.strptime(mw_order.custom_properties[u"PICKUP_TIME"].value, u"%Y-%m-%d %H:%M:%S")

                now = datetime.utcnow()
                if now > order.pickup_time:
                    order.status = OrderStatus.Danger

                elif now + timedelta(minutes=5) > order.pickup_time:
                    order.status = OrderStatus.Warning
            else:
                order.status = OrderStatus.NotSet

            if u"PARTNER" in mw_order.custom_properties:
                order.partner = mw_order.custom_properties[u"PARTNER"].value

            if u"ORIGINATOR_ID" in mw_order.custom_properties:
                order.originator_id = mw_order.custom_properties[u"ORIGINATOR_ID"].value

            if u"SHORT_REFERENCE" in mw_order.custom_properties:
                order.short_reference = mw_order.custom_properties[u"SHORT_REFERENCE"].value

            # address info
            if u"CITY" in mw_order.custom_properties:
                order.city = mw_order.custom_properties[u"CITY"].value

            if u"STATE" in mw_order.custom_properties:
                order.state = mw_order.custom_properties[u"STATE"].value

            if u"COMPLEMENT" in mw_order.custom_properties:
                order.complement = mw_order.custom_properties[u"COMPLEMENT"].value

            if u"FORMATTED_ADDRESS" in mw_order.custom_properties:
                order.address = mw_order.custom_properties[u"FORMATTED_ADDRESS"].value

            if u"NEIGHBORHOOD" in mw_order.custom_properties:
                order.neighborhood = mw_order.custom_properties[u"NEIGHBORHOOD"].value

            if u"POSTAL_CODE" in mw_order.custom_properties:
                order.postal = mw_order.custom_properties[u"POSTAL_CODE"].value

            if u"REFERENCE" in mw_order.custom_properties:
                order.reference = mw_order.custom_properties[u"REFERENCE"].value

            if ignore_items:
                order.items = mw_order.order_items
            else:
                order.items = self.items_creator.create_items(mw_order.order_items)

            all_orders.append(order)

        return all_orders

    def confirm_canceled_order(self, order_id, remote_order_id):
        self.canceled_order_repository.mark_order_as_sent(order_id, remote_order_id)

    def set_order_custom_property(self, order_id, key, value):
        # type: (int, unicode, unicode) -> None
        self.remote_order_taker.set_order_custom_property(order_id, key, value)
        
    def get_retry_order_custom_property(self, order_id, key):
        # type: (int, unicode) -> None
        retry_count = 0
        
        try:
            retry_count_resp = self.remote_order_taker.get_order_custom_property(key, order_id)
            if retry_count_resp is not None:
                retry_count_xml = eTree.XML(retry_count_resp)
                order_property = retry_count_xml.find("OrderProperty")
                if order_property is not None:
                    retry_count = int(order_property.get("value"))
        except Exception as _:
            pass

        return retry_count
    
    def get_order_custom_property(self, order_id, key):
        custom_property = self.remote_order_taker.get_order_custom_property(key, order_id)
        if custom_property is not None:
            retry_count_xml = eTree.XML(custom_property)
            order_property = retry_count_xml.find("OrderProperty")
            if order_property is not None:
                return order_property.get("value")
            
        return None
        
    def is_order_produced(self, order_id):
        return self.order_repository.is_order_produced(order_id)
        
    def get_remote_order_id_by_order_id(self, order_id):
        _, remote_order_id, _ = self.order_repository.get_remote_order_info(order_id)
        return remote_order_id
    
    def get_order_id_by_logistic_id(self, logistic_id):
        # type: (str) -> int
        order_id = self.order_repository.get_order_id_by_logistic_id(logistic_id)
        if order_id:
            return order_id
        
        raise LogisticException("An order associated with the Logistic Id {} does not exist".format(logistic_id))
