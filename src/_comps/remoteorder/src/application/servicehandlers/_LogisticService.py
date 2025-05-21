import json
from logging import getLogger
from typing import Any

from application.customexception import LogisticException
from application.model import LogisticRequestCustomer, LogisticRequestLocation, LogisticRequest, DispatchedEvents, \
    RemoteOrderModelJsonEncoder, LogisticIntegrationStatus, LogisticCancelRequest, LogisticConfirmRequest
from application.services import OrderService
from cfgtools import Configuration
from msgbus import MBEasyContext
from sysactions import get_model, translate_message

logger = getLogger(__name__)


class LogisticService:
    def __init__(self, mb_context, pos_id, order_service, store_id, config):
        # type: (MBEasyContext, int, OrderService, str, Configuration) -> None
        self.order_service = order_service
        self.store_id = store_id

        self.event_dispatcher = DispatchedEvents(mb_context)
        self.automatic_logistic = (config.find_value("RemoteOrder.AutomaticLogistic") or "false").lower() == "true"
        self.logistic_partners = config.find_values("RemoteOrder.LogisticPartners")
        self.logistic_partner = self.logistic_partners[0] if self.logistic_partners else None
        
        self.concurrent_events_lock = None
        self.model = get_model(pos_id)
        
    def set_concurrent_events_lock(self, concurrent_events_lock):
        self.concurrent_events_lock = concurrent_events_lock

    def request_logistic(self, order_id):
        # type: (int) -> None
        
        if not self.logistic_partners:
            raise LogisticException("No Logistic Partner Configured")
        
        order = self.order_service.get_order(order_id)
        logistic_partner = self._get_logistic_partner(order)

        logistic_request = self._get_logistic_request(order, logistic_partner)
        data = json.dumps(logistic_request, encoding="utf-8", cls=RemoteOrderModelJsonEncoder)
        self.event_dispatcher.send_event(DispatchedEvents.LogisticRequest, "", data)
        self.set_integration_status_custom_property(order_id, LogisticIntegrationStatus.SEARCHING)

    def cancel_logistic(self, order_id):
        order = self.order_service.get_order(order_id)
        logistic_cancel_request = self._get_cancel_request(order)
        self.set_integration_status_custom_property(
            order_id, LogisticIntegrationStatus.WAITING_LOGISTIC_CANCEL_RESPONSE)

        if logistic_cancel_request:
            data = json.dumps(logistic_cancel_request, encoding="utf-8", cls=RemoteOrderModelJsonEncoder)
            self.event_dispatcher.send_event(DispatchedEvents.LogisticCancel, "", data)
        else:
            self.logistic_canceled(None, order_id)

    def set_logistic_searching_status(self, remote_order_id, logistic_id):
        # type: (str, str) -> None
        
        order_id = self.order_service.get_order_id(remote_order_id)
        
        if self._get_logistic_status(order_id) != LogisticIntegrationStatus.CONFIRMED:
            self.set_integration_status_custom_property(order_id, LogisticIntegrationStatus.WAITING_SEARCHING_RESPONSE)
            self._set_logistic_id_custom_property(order_id, logistic_id)
    
    def logistic_found(self, logistic_id, remote_order_id, adapter_logistic_id, data):
        order_id = self.order_service.get_order_id(remote_order_id)
        self.order_service.set_order_custom_property(order_id, "LOGISTIC_ID", logistic_id)
        self.order_service.set_order_custom_property(order_id, "ADAPTER_LOGISTIC_ID", adapter_logistic_id)
        self.set_integration_status_custom_property(order_id, LogisticIntegrationStatus.WAITING_CONFIRM_RESPONSE)
        self.event_dispatcher.send_event(DispatchedEvents.LogisticFoundAck, "", data)

    def logistic_confirm(self, remote_order_id):
        order_id = self.order_service.get_order_id(remote_order_id)
        self.set_integration_status_custom_property(order_id, LogisticIntegrationStatus.CONFIRMED)
        
    def send_logistic_confirm(self, order_id):
        order = self.order_service.get_order(order_id)
        logistic_confirm_request = self._get_logistic_confirm_request(order)
        if logistic_confirm_request:
            data = json.dumps(logistic_confirm_request, encoding="utf-8", cls=RemoteOrderModelJsonEncoder)
            self.event_dispatcher.send_event(DispatchedEvents.PosLogisticConfirm, "", data)
    
    def logistic_not_found(self, remote_order_id):
        order_id = self.order_service.get_order_id(remote_order_id)
        self.set_integration_status_custom_property(order_id, LogisticIntegrationStatus.NOT_FOUND)
        
    def logistic_canceled(self, logistic_id, order_id=None):
        if not order_id:
            order_id = self.order_service.get_order_id_by_logistic_id(logistic_id)
            
        self.set_integration_status_custom_property(order_id, LogisticIntegrationStatus.CANCELED)

    def logistic_send(self, order_id):
        self.set_integration_status_custom_property(order_id, LogisticIntegrationStatus.SENT)
        
    def logistic_finished(self, logistic_id, data):
        order_id = self.order_service.get_order_id_by_logistic_id(logistic_id)
        self.set_integration_status_custom_property(order_id, LogisticIntegrationStatus.FINISHED)
        self.event_dispatcher.send_event(DispatchedEvents.LogisticFinishedAck, "", data)
        
    def set_order_to_search_logistic(self, order_id, logistic_partner):
        self.set_integration_status_custom_property(order_id, LogisticIntegrationStatus.NEED_SEARCH)
        self.set_adapter_logistic_name_custom_property(order_id, logistic_partner)
        
    def set_integration_status_custom_property(self, order_id, status):
        with self.concurrent_events_lock:
            self.order_service.set_order_custom_property(order_id, "LOGISTIC_INTEGRATION_STATUS", status)
            
    def set_adapter_logistic_name_custom_property(self, order_id, status):
        with self.concurrent_events_lock:
            self.order_service.set_order_custom_property(order_id, "ADAPTER_LOGISTIC_NAME", status)
            
    def set_delivery_status_custom_property(self, order_id, name):
        with self.concurrent_events_lock:
            self.order_service.set_order_custom_property(order_id, "DELIVERY_INTEGRATION_STATUS", name)
            
    def _set_logistic_id_custom_property(self, order_id, logistic_id):
        with self.concurrent_events_lock:
            self.order_service.set_order_custom_property(order_id, "LOGISTIC_ID", logistic_id)

    def _get_logistic_request(self, order, logistic_partner):
        logistic_request = LogisticRequest(order.remote_id,
                                           logistic_partner,
                                           self.store_id,
                                           order.short_reference,
                                           LogisticRequestLocation(),
                                           LogisticRequestCustomer())
        logistic_request.customer.name = order.customer_name
        
        remote_order_json = order.custom_properties["REMOTE_ORDER_JSON"]
        remote_order = json.loads(remote_order_json)
        custom_properties = remote_order.get("custom_properties", None)
        if custom_properties:
            custom_properties_dict = {item['key']: item['value'] for item in custom_properties}  # type: Any
            
            logistic_request.customer.phone = custom_properties_dict.get("customer_phone", "")
            pickup = remote_order.get("pickup")
            if pickup:
                address = pickup.get("address")
                if address:
                    logistic_request.delivery_location.latitude = address.get("latitude", "")
                    logistic_request.delivery_location.longitude = address.get("longitude", "")
                    logistic_request.delivery_location.street = address.get("streetName", "")
                    logistic_request.delivery_location.number = address.get("streetNumber", "")
                    logistic_request.delivery_location.neighborhood = address.get("neighborhood", "")
                    logistic_request.delivery_location.city = address.get("city", "")
                    logistic_request.delivery_location.state = address.get("state", "")
                    logistic_request.delivery_location.cep = address.get("postalCode", "")
                    logistic_request.delivery_location.country = address.get("country", "")
                    logistic_request.delivery_location.complement = address.get("complement", "")
    
        return logistic_request
    
    def _get_cancel_request(self, order):
        logistic_id = self.order_service.get_order_custom_property(order.id, "LOGISTIC_ID")
        if not logistic_id:
            logger.info("Logistic Id not Found")
            return None
        
        return LogisticCancelRequest(logistic_id, self.store_id)

    def _get_logistic_confirm_request(self, order):
        adapter_logistic_name = self._get_logistic_adapter_name(order.id)
        adapter_logistic_name = self._translate_partner_name(adapter_logistic_name)
        return LogisticConfirmRequest(order.remote_id, adapter_logistic_name, self._get_adapter_logistic_id(order.id))
    
    def _get_logistic_partner(self, order):
        logistic_partner = self._get_logistic_adapter_name(order.id)
        if not logistic_partner:
            logistic_partner = self.logistic_partner
            
        return logistic_partner

    def _get_logistic_status(self, order_id):
        return self.order_service.get_order_custom_property(order_id, "LOGISTIC_INTEGRATION_STATUS")
    
    def _get_adapter_logistic_id(self, order_id):
        return self.order_service.get_order_custom_property(order_id, "ADAPTER_LOGISTIC_ID")
    
    def _get_logistic_adapter_name(self, order_id):
        return self.order_service.get_order_custom_property(order_id, "ADAPTER_LOGISTIC_NAME") or self.logistic_partner

    def set_deliveryman_data(self, order_id, data):
        return self.order_service.set_order_custom_property(order_id, "LOGISTIC_DELIVERYMAN_DATA", data)
    
    def _translate_partner_name(self, partner_name):
        try:
            if self.model and partner_name:
                partner_name = translate_message(self.model, "LOGISTIC_PARTNER_" + str(partner_name).upper())
        except Exception as _:
            pass

        return partner_name
