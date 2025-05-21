# -*- coding: utf-8 -*-

import logging
import time
from threading import Thread

from application.customexception import OrderError
from application.model import DispatchedEvents, OrderToCancel
from mwhelper import BaseRepository

logger = logging.getLogger("CanceledOrdersThread")

SERVICE_NAME = "DeliveryPersistence"


class CanceledOrderRepository(BaseRepository):

    def __init__(self, mb_context, pos_id, interval_to_send, cancel_order_on_partner):
        super(CanceledOrderRepository, self).__init__(mb_context)
        self.pos_id = pos_id
        self.interval_to_send = interval_to_send
        self.cancel_order_on_partner = cancel_order_on_partner
        
        self.event_dispatcher = DispatchedEvents(mb_context)
        if interval_to_send > 0:
            sac_sync_thread = Thread(target=self._send_canceled_order_data_to_sac, name="SAC Sync")
            sac_sync_thread.daemon = True
            sac_sync_thread.start()

    def add_canceled_order(self, order_id, reason, manual_cancel=False):
        try:
            remote_order_id = self._get_remote_order_id(order_id)
            sent_to_sac = 0 if self.cancel_order_on_partner or manual_cancel else -1
            reason = "8|" + reason if not manual_cancel else "11|" + reason

            def inner_func(conn):
                query = """
                INSERT OR REPLACE INTO CanceledOrders VALUES ('{}', '{}', '{}', {})
                """.format(order_id, remote_order_id, reason, sent_to_sac)
                conn.query(query)

            self.execute_with_connection(inner_func, service_name=SERVICE_NAME)
        except Exception as _:
            pass

    def pick_pending_order(self):
        def inner_func(conn):
            orders_to_cancel = []
            
            query = """
                        SELECT RemoteOrderId, Reason
                        FROM CanceledOrders
                        WHERE SentToSAC = 0
                    """
            for row in conn.select(query):
                orders_to_cancel.append(OrderToCancel(row.get_entry(0), row.get_entry(1)))
                
            return orders_to_cancel
        return self.execute_with_connection(inner_func, service_name=SERVICE_NAME)

    def mark_order_as_sent(self, order_id='', remote_order_id=''):
        def inner_func(conn):
            query = """
            UPDATE CanceledOrders
            SET SentToSAC = 1
            WHERE OrderId = '{}'
              OR RemoteOrderId = '{}'
            """.format(order_id, remote_order_id)
            conn.query(query)
        self.execute_with_connection(inner_func, service_name=SERVICE_NAME)

    def _get_remote_order_id(self, order_id):
        def inner_func(conn):
            query = """
            SELECT Value
            FROM OrderCustomProperties
            WHERE OrderId = '{}'
              AND Key = 'REMOTE_ORDER_ID' 
            """.format(order_id)
            for row in conn.select(query):
                return row.get_entry(0)
        return self.execute_with_connection(inner_func, db_name=str(self.pos_id))

    def _send_canceled_order_data_to_sac(self):
        logger.debug('Thread started')
        while True:
            try:
                orders_to_cancel = self.pick_pending_order()
                for order in orders_to_cancel:
                    cancel_message = 'Canceling order: RemoteOrderId: {}; Reason: {}'
                    logger.debug(cancel_message.format(order.remote_order_id, order.reason))
                    error_code = order.reason.split("|")[0]
                    reason = order.reason.split("|")[1]
                    order_error = OrderError(order.remote_order_id, error_code, reason)
                    self.event_dispatcher.send_pos_order_cancel_to_server(order_error)
                        
                time.sleep(self.interval_to_send)
            except Exception as _:
                logger.exception("Error sending canceled order to SAC")
            finally:
                time.sleep(self.interval_to_send)
