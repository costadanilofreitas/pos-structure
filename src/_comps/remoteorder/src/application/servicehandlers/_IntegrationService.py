# -*- coding: utf-8 -*-
import json

from application.customexception import StoreClosedException, OrderError, InvalidOrderException, ValidationException, \
    PaymentException, FiscalException, OrderException
from application.model import DispatchedEvents, ProcessedOrder, ErrorStatus, DeliveryIntegrationStatus, \
    LogisticIntegrationStatus
from application.util import get_encoded_json


class IntegrationService(object):
    def __init__(self, model, store_service, remote_order_processor, order_service, cancellation_service,
                 event_dispatcher, cancel_order_on_partner, mandatory_logistic_for_integration, concurrent_events_lock,
                 logger):
        self.model = model
        self.store_service = store_service
        self.remote_order_processor = remote_order_processor
        self.order_service = order_service
        self.cancellation_service = cancellation_service
        self.event_dispatcher = event_dispatcher
        self.cancel_order_on_partner = cancel_order_on_partner
        self.mandatory_logistic_for_integration = mandatory_logistic_for_integration
        self.concurrent_events_lock = concurrent_events_lock
        self.logger = logger

    def create_order(self, delivery_json, unavailable_items):
        parsed_order = None
        order_id = None
        remote_order_id = self._get_remote_order_id(delivery_json)
        
        self.logger.info("Creating order for RemoteOrderId: {}".format(remote_order_id))
        
        try:
            self._check_store_is_opened()
            self._check_business_period()
        
            parsed_order = self._parse_order(delivery_json)
            order_id, processed_order_json = self._create_order(delivery_json, parsed_order, unavailable_items)
            self._save_remote_order_json(delivery_json, order_id)
            self._confirm_order(order_id, parsed_order, processed_order_json)
        except StoreClosedException as ex:
            self.logger.info("The Store is closed. RemoteOrderId: {}".format(remote_order_id))
            order_error = OrderError(remote_order_id, ex.error_code, ex.message, type(ex).__name__, self.model)
            self.store_service.dispatch_store_status_event()
            self.event_dispatcher.send_pos_order_cancel_to_server(order_error)
            raise
        except Exception as ex:
            self.logger.exception("Exception creating order for RemoteOrderId: {}".format(remote_order_id))
            self._handle_create_order_exception(delivery_json, order_id, remote_order_id, parsed_order, ex)
    
        return order_id

    def _confirm_order(self, order_id, parsed_order, processed_order_json):
        if not parsed_order.need_logistics:
            self._save_integration_status(order_id,
                                          DeliveryIntegrationStatus.CONFIRMED,
                                          LogisticIntegrationStatus.RECEIVED)
            self.event_dispatcher.send_event(DispatchedEvents.PosOrderConfirm, "", processed_order_json)
            
        elif not self.mandatory_logistic_for_integration:
            self._save_integration_status(order_id,
                                          DeliveryIntegrationStatus.CONFIRMED,
                                          LogisticIntegrationStatus.WAITING)
            self.event_dispatcher.send_event(DispatchedEvents.PosOrderConfirm, "", processed_order_json)
            
        else:
            self._save_integration_status(order_id,
                                          DeliveryIntegrationStatus.RECEIVED,
                                          LogisticIntegrationStatus.NEED_SEARCH)
            self.event_dispatcher.send_event(DispatchedEvents.PosOrderReceived, "", processed_order_json)

    def _check_store_is_opened(self):
        self.store_service.check_store_is_opened()
            
    def _check_business_period(self):
        with self.concurrent_events_lock:
            self.remote_order_processor.check_business_period()

    def _parse_order(self, remote_order_json, minimum=False):
        return self.remote_order_processor.parse_order(remote_order_json, minimum)
    
    def _create_order(self, data, remote_order, unavailable_items):
        with self.concurrent_events_lock:
            remote_order_id, processed_order = self.remote_order_processor.process_order(unavailable_items,
                                                                                         remote_order)
            processed_order_json = get_encoded_json(processed_order)
    
            order_id = json.loads(processed_order_json)["localOrderId"]
            partner = json.loads(data)["partner"]
            message = "New order created. Partner: {}; OrderId: {}; RemoteOrderId: {}"
            self.logger.info(message.format(partner, order_id, remote_order_id))
    
            return order_id, processed_order_json

    def _handle_create_order_exception(self, delivery_json, order_id, remote_order_id, parsed_order, exception):
        order_error = None
        processed_order = None
    
        try:
            if not self.cancel_order_on_partner:
                order_id, processed_order = self._create_error_order(delivery_json, parsed_order, remote_order_id)

            raise exception
        except (InvalidOrderException, ValidationException, PaymentException, FiscalException, OrderException) as ex:
            message = ex.i18n_tag if ex.i18n_tag else ex.message
            order_error = OrderError(remote_order_id, ex.error_code, message, type(ex).__name__, self.model)
            raise
        except BaseException as ex:
            order_error = OrderError(remote_order_id, ErrorStatus.UNEXPECTED_ERROR, ex.message, "Unknown", self.model)
            raise
        finally:
            if not self.cancel_order_on_partner:
                self._handle_order_error(delivery_json, order_error, order_id, processed_order, remote_order_id)
            else:
                self.logger.info("Canceling RemoteOrderId: {} on partner".format(remote_order_id))
                self.event_dispatcher.send_pos_order_cancel_to_server(order_error)
                
                if order_id:
                    self.cancellation_service.save_cancellation_reason_on_custom_properties(order_id)

    def _handle_order_error(self, delivery_json, order_error, order_id, processed_order, remote_order_id):
        if not order_error:
            return
        
        error_description = self.order_service.get_order_custom_property(order_id, "DELIVERY_ERROR_DESCRIPTION")
        if not error_description:
            self._save_integration_error_on_custom_properties(delivery_json,
                                                              order_error.message,
                                                              order_error.error_type,
                                                              order_id)
        else:
            order_error.message = error_description
            error_type = self.order_service.get_order_custom_property(order_id, "DELIVERY_ERROR_TYPE")
            if error_type:
                order_error.error_type = error_type
    
        self._confirm_order_with_error(order_id, order_error, processed_order, remote_order_id)

    def _create_error_order(self, delivery_json, parsed_order, remote_order_id):
        self.logger.info("Saving error order for RemoteOrderId: {}".format(remote_order_id))
        if parsed_order is None:
            parsed_order = self._parse_order(delivery_json, True)
            
        try:
            order_id = self.order_service.get_order_id(remote_order_id)
            self.logger.info("Voided order already exists for RemoteOrderId: {}".format(remote_order_id))
        except Exception as _:
            self.logger.info("Saving void order for RemoteOrderId: {}".format(remote_order_id))
            order_id = self._save_error_order(parsed_order)
            
        self._save_remote_order_json(delivery_json, order_id)

        processed_order = ProcessedOrder(parsed_order.id, order_id, [])
        return order_id, processed_order

    def _save_error_order(self, parsed_order):
        with self.concurrent_events_lock:
            return self.remote_order_processor.save_error_order(parsed_order)
    
    def _save_integration_error_on_custom_properties(self, delivery_json, error_description, error_type, order_id):
        with self.concurrent_events_lock:
            if not order_id:
                remote_order = self._parse_order(delivery_json, minimum=True)
                order_id = self.remote_order_processor.get_local_order_id(remote_order)
            if error_type and order_id:
                self.order_service.set_order_custom_property(order_id, "DELIVERY_ERROR_TYPE", error_type.upper())
                self.order_service.set_order_custom_property(order_id, "DELIVERY_ERROR_DESCRIPTION", error_description)
            
    def _confirm_order_with_error(self, order_id, order_error, processed_order, remote_order_id):
        if not processed_order:
            return
            
        log_message = "Confirming order: {} with error on partner for RemoteOrderId: {}"
        self.logger.info(log_message.format(order_id, remote_order_id))
        
        processed_order.has_error = True
        processed_order.code = order_error.error_code
        processed_order.error_message = order_error.message
        processed_order_json = get_encoded_json(processed_order)
        self._save_integration_status(order_id,
                                      DeliveryIntegrationStatus.CONFIRMED_WITH_ERROR,
                                      LogisticIntegrationStatus.WAITING)
        self.event_dispatcher.send_event(DispatchedEvents.PosOrderConfirm, "", processed_order_json)
        
    def _save_integration_status(self, order_id, delivery_status, logistic_status):
        with self.concurrent_events_lock:
            self.order_service.set_order_custom_property(order_id, "DELIVERY_INTEGRATION_STATUS", delivery_status)
            self.order_service.set_order_custom_property(order_id, "LOGISTIC_INTEGRATION_STATUS", logistic_status)

    def _save_remote_order_json(self, delivery_json, order_id):
        if order_id:
            self.order_service.set_order_custom_property(order_id, "REMOTE_ORDER_JSON", delivery_json)

    @staticmethod
    def _get_remote_order_id(data):
        remote_order_id = None
        try:
            parsed_json = json.loads(data)
            if "id" in parsed_json:
                remote_order_id = parsed_json["id"]
        except ValueError:
            pass
    
        return remote_order_id
