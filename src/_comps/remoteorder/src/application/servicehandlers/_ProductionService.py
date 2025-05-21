# -*- coding: utf-8 -*-
from application.customexception import ValidationException, OrderException, FiscalException, OrderError, \
    LogisticException
from application.model import ErrorStatus, LogisticIntegrationStatus
from application.services import Printer


class ProductionService(object):
    def __init__(self, pos_id, mb_context, model, remote_order_pos_id, order_service, cancellation_service,
                 event_dispatcher, mandatory_logistic_for_production, cancel_order_on_partner, print_delivery_coupon,
                 concurrent_events_lock, logger):
        self.pos_id = pos_id
        self.mb_context = mb_context
        self.model = model
        self.remote_order_pos_id = remote_order_pos_id
        self.order_service = order_service
        self.cancellation_service = cancellation_service
        self.event_dispatcher = event_dispatcher
        self.mandatory_logistic_for_production = mandatory_logistic_for_production
        self.cancel_order_on_partner = cancel_order_on_partner
        self.print_delivery_coupon = print_delivery_coupon
        self.concurrent_events_lock = concurrent_events_lock
        self.logger = logger
        
        self.printer = Printer(self.mb_context, self.pos_id, self.logger, [self.remote_order_pos_id])
        
    def auto_produce_order(self, order_id):
        if self._is_schedule_order(order_id):
            self.logger.info("OrderId: {} is a scheduling order. It will not be produced automatically")
            return
        
        self.produce_order(order_id)
        
    def produce_order(self, order_id):
        remote_order_id = None
        
        try:
            remote_order_id = self.order_service.get_remote_order_id_by_order_id(order_id)
            self.logger.info("Producing order for RemoteOrderId: {}".format(remote_order_id))

            self._validate_logistic(order_id)
            self._produce_remote_order(order_id)
            self._print_delivery_coupon(order_id, remote_order_id)
        except LogisticException as _:
            self.logger.exception("There is no logistic confirmed for RemoteOrderId: {}".format(remote_order_id))
            raise
        except Exception as ex:
            self.logger.exception("Exception creating order for RemoteOrderId: {}".format(remote_order_id))
            self._handle_producing_order_exception(order_id, remote_order_id, ex)

    def _validate_logistic(self, order_id):
        if self.mandatory_logistic_for_production:
            logistic_status = self.order_service.get_order_custom_property(order_id, "LOGISTIC_INTEGRATION_STATUS")
            if not LogisticIntegrationStatus.is_final_status(logistic_status):
                if logistic_status != LogisticIntegrationStatus.SEARCHING:
                    self._save_need_logistic_integration_status(order_id)
            
                raise LogisticException("$MANDATORY_LOGISTIC_FOR_PRODUCTION")

    def _handle_producing_order_exception(self, order_id, remote_order_id, exception):
        order_error = None
        try:
            raise exception
        except (ValidationException, OrderException, FiscalException) as ex:
            message = ex.i18n_tag if ex.i18n_tag else ex.message
            order_error = OrderError(remote_order_id, ex.error_code, message, type(ex).__name__, self.model)
            raise
        except BaseException as ex:
            order_error = OrderError(remote_order_id, ErrorStatus.UNEXPECTED_ERROR, ex.message, "Unknown", self.model)
            raise
        finally:
            if order_error:
                retry_count = self.order_service.get_retry_order_custom_property(order_id, "PRODUCE_RETRY_COUNT")
                
                retry_count += 1
                self.order_service.set_order_custom_property(order_id, "PRODUCE_RETRY_COUNT", str(retry_count))
                if retry_count >= 3:
                    max_retries_reached_message = "Max retries reached on Production for RemoteOrderId: {}"
                    if not self.cancel_order_on_partner:
                        self.logger.info(max_retries_reached_message.format(remote_order_id))
                        self._save_production_error_on_custom_properties(order_error.message,
                                                                         order_error.error_type,
                                                                         order_id)
                    else:
                        self.logger.info("Canceling RemoteOrderId: {} on partner".format(remote_order_id))
                        self.event_dispatcher.send_pos_order_cancel_to_server(order_error)

                        if order_id:
                            self.cancellation_service.save_cancellation_reason_on_custom_properties(order_id)

                retrying_message = "Retry count {} for RemoteOrderId: {}. Retrying"
                self.logger.info(retrying_message.format(retry_count, remote_order_id))
    
    def _produce_remote_order(self, order_id):
        with self.concurrent_events_lock:
            self.order_service.send_order_to_production(order_id)

    def _save_production_error_on_custom_properties(self, error_description, error_type, order_id):
        with self.concurrent_events_lock:
            if error_type and order_id:
                self.order_service.set_order_custom_property(order_id, "DELIVERY_ERROR_TYPE", error_type.upper())
                self.order_service.set_order_custom_property(order_id, "DELIVERY_ERROR_DESCRIPTION", error_description)
                
    def _save_need_logistic_integration_status(self, order_id):
        with self.concurrent_events_lock:
            self.order_service.set_order_custom_property(order_id,
                                                         "LOGISTIC_INTEGRATION_STATUS",
                                                         LogisticIntegrationStatus.NEED_SEARCH)
                
    def _print_delivery_coupon(self, order_id, remote_order_id):
        try:
            if self.print_delivery_coupon:
                self.logger.info("Printing delivery coupon for RemoteOrderId: {}".format(remote_order_id))
                self.printer.print_delivery_report(order_id)
        except Exception as _:
            self.logger.exception("Error Printing delivery coupon for RemoteOrderId: {}".format(remote_order_id))

    def _is_schedule_order(self, order_id):
        remote_order = self.order_service.get_order(order_id)
        if "SCHEDULE_TIME" in remote_order.custom_properties:
            return True
        
        return False
