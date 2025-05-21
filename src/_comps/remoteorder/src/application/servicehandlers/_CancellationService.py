# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta

from application.customexception import InvalidSonException, OrderNotFoundException, OrderError, CancelException
from application.model import DispatchedEvents, DeliveryIntegrationStatus, LogisticIntegrationStatus, ErrorStatus
from application.util import get_encoded_json, convert_from_utf_to_localtime


class CancellationService(object):
    def __init__(self, model, order_service, canceled_order_repository, max_time_to_cancel_orders, event_dispatcher,
                 concurrent_events_lock, logger):
        self.model = model
        self.order_service = order_service
        self.canceled_order_repository = canceled_order_repository
        self.max_time_to_cancel_orders = max_time_to_cancel_orders
        self.event_dispatcher = event_dispatcher
        self.concurrent_events_lock = concurrent_events_lock
        self.logger = logger
        
    def trigger_manual_cancel_event(self, remote_order_id):
        order_id = self.order_service.get_order_id(remote_order_id)
        self._validate_time_before_cancel(order_id)
        
        order_error = OrderError(order_id, ErrorStatus.MANUAL_CANCEL, "$MANUAL_CANCEL", model=self.model)
        self.canceled_order_repository.add_canceled_order(order_id, order_error.message, True)
        self.save_cancellation_reason_on_custom_properties(order_id)
        self.order_service.cancel_order(remote_order_id)
    
    def cancel_order(self, data):
        sac_order_cancel_data = json.loads(data, encoding="utf-8")
        remote_order_id = sac_order_cancel_data["id"]
        order_id = None

        self.logger.info("Cancelling order for RemoteOrderId: {}".format(remote_order_id))
        try:
            order_id = self.order_service.get_order_id(remote_order_id)
            if self._cancel_order(remote_order_id, order_id):
                self.logger.info("Order canceled on POS for RemoteOrderId: {}".format(remote_order_id))

                self._save_canceled_integration_status(order_id)
                self._send_pos_order_cancel_ack(data, remote_order_id)
        except Exception as ex:
            self.logger.exception("Exception canceling order for RemoteOrderId: {}".format(remote_order_id))
            self._handle_cancelling_order_exception(order_id, remote_order_id, data, ex)

    def _save_canceled_integration_status(self, order_id):
        with self.concurrent_events_lock:
            self.order_service.set_order_custom_property(order_id,
                                                         "DELIVERY_INTEGRATION_STATUS",
                                                         DeliveryIntegrationStatus.CANCELED)

    def save_cancellation_reason_on_custom_properties(self, order_id):
        with self.concurrent_events_lock:
            self.order_service.set_order_custom_property(order_id, "VOID_REASON_ID", "4")
            self.order_service.set_order_custom_property(order_id, "VOID_REASON_DESCR", "4 - Cancelamento")

    def _handle_cancelling_order_exception(self, order_id, remote_order_id, data, original_exception):
        try:
            raise original_exception
        except OrderNotFoundException as _:
            self._send_pos_order_cancel_ack(data, remote_order_id)
        except InvalidSonException as ex:
            order_error = OrderError(remote_order_id, ex.error_code, ex.message)
            self._send_pos_order_cancel_error(order_id, remote_order_id, order_error)
            raise
        except Exception as ex:
            order_error = ex if isinstance(ex, OrderError) else OrderError(remote_order_id, 99, ex.message)
            self._send_pos_order_cancel_error(order_id, remote_order_id, order_error)
            raise
        
    def _cancel_order(self, remote_order_id, order_id):
        with self.concurrent_events_lock:
            if self.order_service.cancel_order(remote_order_id):
                self.order_service.confirm_canceled_order(order_id, remote_order_id)
                return True
            
        return False

    def _send_pos_order_cancel_error(self, order_id, remote_order_id, order_error):
        retry_count = self.order_service.get_retry_order_custom_property(order_id, "CANCEL_RETRY_COUNT")
    
        retry_count += 1
        self.order_service.set_order_custom_property(order_id, "CANCEL_RETRY_COUNT", str(retry_count))
        if retry_count >= 3:
            max_retries_reached_message = "Max retries reached for RemoteOrderId: {}. " \
                                          "Sending PosOrderCancelError for partner"
            self.logger.info(max_retries_reached_message.format(remote_order_id))
            
            self.order_service.confirm_canceled_order(order_id, remote_order_id)
            order_error_json = get_encoded_json(order_error)
            self.event_dispatcher.send_event(DispatchedEvents.PosOrderCancelError, "", order_error_json)
        
    def _send_pos_order_cancel_ack(self, order_cancel, remote_order_id):
        self.logger.info("Sending PosOrderCancelAck for RemoteOrderId: {}".format(remote_order_id))
        self.event_dispatcher.send_event(DispatchedEvents.PosOrderCancelAck, "", order_cancel)
            
    def _validate_time_before_cancel(self, order_id):
        order_type = self.order_service.get_order_custom_property(order_id, "ORDER_TYPE")
        if order_type is not None:
            formatted_time = self._get_formatted_time(order_id, order_type)
            since_datetime = datetime.now() - timedelta(hours=self.max_time_to_cancel_orders)
            if formatted_time and convert_from_utf_to_localtime(formatted_time).replace(tzinfo=None) < since_datetime:
                raise CancelException("$NOT_POSSIBLE_TO_CANCEL_DELIVERY", self.model)

    def _get_formatted_time(self, order_id, order_type):
        time = self.order_service.get_order_custom_property(order_id, "CREATED_AT")
        if order_type == "A":
            time = self.order_service.get_order_custom_property(order_id, "SCHEDULE_TIME")
        
        return datetime.strptime(time, "%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _get_data_info(data):
        remote_order_id = None
        originator = None
        try:
            parsed_json = json.loads(data)
            if "id" in parsed_json:
                remote_order_id = parsed_json["id"]
            if "custom_params" in parsed_json and "ORIGINATOR" in parsed_json["custom_params"]:
                originator = parsed_json["custom_params"]["ORIGINATOR"]
        except ValueError:
            pass
    
        return remote_order_id, originator
