# -*- coding: utf-8 -*-
import json
import logging
import time
from datetime import datetime, timedelta
from threading import Thread

from application.customexception import OrderError
from application.model import DispatchedEvents, LogisticIntegrationStatus, ErrorStatus, RemoteOrderModelJsonEncoder, \
    DeliveryIntegrationStatus
from application.util import get_encoded_json
from mwhelper import BaseRepository
from sysactions import get_model

logger = logging.getLogger("LogisticsThreads")


class LogisticRepository(BaseRepository):
    def __init__(self, mb_context, pos_id, order_service, remote_order_processor, logistic_service, config):
        super(LogisticRepository, self).__init__(mb_context)
        self.pos_id = pos_id
        self.order_service = order_service
        self.remote_order_processor = remote_order_processor
        self.logistic_service = logistic_service

        time_to_cancel_order_without_logistic = config.find_value("RemoteOrder.TimeToCancelOrdersWithoutLogistic") or 5
        self.time_to_cancel_order_without_logistic = int(time_to_cancel_order_without_logistic)
        self.interval_to_send = float(config.find_value("RemoteOrder.LogisticThreadsRunTime") or 10)
        self.automatic_logistic = str(config.find_value("RemoteOrder.AutomaticLogistic") or "false").lower() == 'true'

        self.model = get_model(pos_id)
        self.event_dispatcher = DispatchedEvents(mb_context)
        if self.interval_to_send > 0:
            sac_sync_thread = Thread(target=self._run_logistic_functions, name="Delivery Integration")
            sac_sync_thread.daemon = True
            sac_sync_thread.start()
            
    def _run_logistic_functions(self):
        while True:
            try:
                self._verify_delivery_integration()
                self._verify_logistic_integration()
                self._cancel_logistic_from_canceled_orders()
                self._confirm_logistic_orders()
            except Exception as _:
                logger.exception("Error running logistic functions")
            finally:
                time.sleep(self.interval_to_send)

    def _verify_delivery_integration(self):
        try:
            orders_id = self._get_pending_delivery_integration_orders()
            for order_id in orders_id:
                try:
                    order = self.order_service.get_order(order_id)
                    logistic_status = order.custom_properties["LOGISTIC_INTEGRATION_STATUS"]
                    logger.info("Verifying delivery integration for order id {}. Current Status: {}".format(
                            order_id, logistic_status))
                    if LogisticIntegrationStatus.is_final_status(logistic_status):
                        logger.info("Confirming delivery integration for order id {}".format(order_id))
                        self._confirm_order(order, order_id)
                        continue

                    time_to_add = timedelta(minutes=self.time_to_cancel_order_without_logistic)
                    time_to_cancel = order.receive_time + time_to_add
                    if datetime.utcnow() > time_to_cancel:
                        logger.info("Order id {} reached time to cancel without logistic".format(order_id))
                        self._cancel_order(order)
                except Exception as _:
                    logger.exception("Error verifying delivery integration for order id {}".format(order_id))
        except Exception as _:
            logger.exception("Error verifying delivery integration")
                
    def _verify_logistic_integration(self):
        try:
            logistic_orders = self._get_pending_logistic_integration_orders()
            for logistic_order in logistic_orders:
                order_id = ''
                try:
                    order_id = int(logistic_order[0])
                    logistic_status = logistic_order[1]
                    if logistic_status == LogisticIntegrationStatus.CANCELED and not self.automatic_logistic:
                        continue
                        
                    logger.info("Requesting logistic for order id {}".format(order_id))
                    self.logistic_service.request_logistic(order_id)
                except Exception as _:
                    logger.exception("Error verifying logistic integration for order id {}".format(order_id))
                
        except Exception as _:
            logger.exception("Error verifying logistic integration")

    def _cancel_logistic_from_canceled_orders(self):
        try:
            logistic_orders = self._get_pending_logistic_canceling_orders()
            for order_id in logistic_orders:
                try:
                    logger.info("Canceling logistic for order id {}".format(order_id))
                    self.logistic_service.cancel_logistic(order_id)
                except Exception as _:
                    logger.exception("Error canceling logistic for order id {}".format(order_id))
        except Exception as _:
            logger.exception("Error canceling logistic")
            
    def _confirm_logistic_orders(self):
        try:
            logistic_orders = self._get_not_confirmed_logistic_orders()
            for order_id in logistic_orders:
                try:
                    logger.info("Confirming logistic for order id {}".format(order_id))
                    self.logistic_service.send_logistic_confirm(order_id)
                except Exception as _:
                    logger.exception("Error confirming logistic for order id {}".format(order_id))
        except Exception as _:
            logger.exception("Error confirming logistic")

    def _cancel_order(self, order):
        adapter_logistic_name = self.order_service.get_order_custom_property(order.id, "ADAPTER_LOGISTIC_NAME") or ""
        message = "$LOGISTIC_NOT_FOUND|{}".format(adapter_logistic_name)
        order_error = OrderError(order.remote_id, ErrorStatus.LOGISTIC_ERROR, message, model=self.model)
        order_error_json = json.dumps(order_error, encoding="utf-8", cls=RemoteOrderModelJsonEncoder)
        self.event_dispatcher.send_event(DispatchedEvents.PosOrderCancel, "", order_error_json, logger=logger)
        self.logistic_service.set_delivery_status_custom_property(order.id,
                                                                  DeliveryIntegrationStatus.WAITING_CANCEL_RESPONSE)
        self.logistic_service.set_integration_status_custom_property(order.id,
                                                                     LogisticIntegrationStatus.WAITING_CANCEL_RESPONSE)

    def _confirm_order(self, order, order_id):
        processed_order = self.remote_order_processor.get_processed_order(order.remote_id, order_id)
        data = get_encoded_json(processed_order)
        self.event_dispatcher.send_event(DispatchedEvents.PosOrderConfirm, "", data, logger=logger)

    def _get_pending_delivery_integration_orders(self):
        def inner_func(conn):
            orders = []
            query = """
            SELECT o.OrderId
            FROM OrderCustomProperties ocp
            JOIN Orders o ON o.OrderId = ocp.OrderId
            WHERE
                o.StateId IN (2, 5) AND
                ocp.Key = 'DELIVERY_INTEGRATION_STATUS' AND
                ocp.Value = '{}' AND
                o.BusinessPeriod >= strftime('%Y%m%d', datetime('now', '-1 days'), 'localtime')
            """.format(DeliveryIntegrationStatus.RECEIVED)
            for row in conn.select(query):
                orders.append(row.get_entry("OrderId"))
        
            return orders
    
        return self.execute_with_connection(inner_func, db_name=int(self.pos_id))

    def _get_pending_logistic_integration_orders(self):
        def inner_func(conn):
            orders = []
            query = """
            SELECT o.OrderId, ocp.Value
            FROM OrderCustomProperties ocp
            JOIN Orders o ON o.OrderId = ocp.OrderId
            WHERE
            o.StateId IN (2, 5) AND
            ocp.Key = 'LOGISTIC_INTEGRATION_STATUS' AND
            ocp.Value IN ('{}', '{}', '{}') AND
            o.BusinessPeriod >= strftime('%Y%m%d', datetime('now', '-1 days'), 'localtime')
            """.format(LogisticIntegrationStatus.NEED_SEARCH,
                       LogisticIntegrationStatus.CANCELED,
                       LogisticIntegrationStatus.SEARCHING)
            for row in conn.select(query):
                orders.append((row.get_entry("OrderId"), row.get_entry("Value")))
        
            return orders
    
        return self.execute_with_connection(inner_func, db_name=int(self.pos_id))

    def _get_pending_logistic_canceling_orders(self):
        def inner_func(conn):
            orders = []
            query = """
            SELECT o.OrderId
            FROM OrderCustomProperties ocp
            JOIN Orders o ON o.OrderId = ocp.OrderId
            WHERE
            o.StateId == 4 AND
            ocp.Key = 'LOGISTIC_INTEGRATION_STATUS' AND ocp.Value NOT IN ('{}', '{}', '{}') AND
            o.BusinessPeriod >= strftime('%Y%m%d', datetime('now', '-1 days'), 'localtime')
            """.format(
                LogisticIntegrationStatus.CANCELED, LogisticIntegrationStatus.FINISHED, LogisticIntegrationStatus.SENT)
            for row in conn.select(query):
                orders.append(row.get_entry("OrderId"))
        
            return orders
    
        return self.execute_with_connection(inner_func, db_name=int(self.pos_id))

    def _get_not_confirmed_logistic_orders(self):
        def inner_func(conn):
            orders = []
            query = """
            SELECT o.OrderId
            FROM OrderCustomProperties ocp
            JOIN Orders o ON o.OrderId = ocp.OrderId
            WHERE
            o.StateId IN (2, 5) AND
            ocp.Key = 'LOGISTIC_INTEGRATION_STATUS' AND ocp.Value == '{}' AND
            o.BusinessPeriod >= strftime('%Y%m%d', datetime('now', '-1 days'), 'localtime')
            """.format(LogisticIntegrationStatus.WAITING_CONFIRM_RESPONSE)
            for row in conn.select(query):
                orders.append(row.get_entry("OrderId"))
        
            return orders
    
        return self.execute_with_connection(inner_func, db_name=int(self.pos_id))
