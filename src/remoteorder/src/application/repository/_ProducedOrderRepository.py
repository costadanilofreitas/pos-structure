# -*- coding: utf-8 -*-

import logging

from application.customexception import OrderError
from application.model import BusTokens
from msgbus import TK_SYS_ACK, FM_PARAM, MBEasyContext
from mwhelper import BaseRepository

logger = logging.getLogger("ProducedOrdersRepository")

SERVICE_NAME = "DeliveryPersistence"


class ProducedOrderRepository(BaseRepository):

    def __init__(self, pos_id, mb_context):
        # type: (int, MBEasyContext) -> None
        
        super(ProducedOrderRepository, self).__init__(mb_context)
        self.pos_id = pos_id

    def add_produced_order(self, order_id):
        try:
            remote_order_id = self._get_remote_order_id(order_id)
            fiscal_xml = ""
            msg = self.mb_context.MB_EasySendMessage('FiscalWrapper',
                                                     BusTokens.TK_FISCALWRAPPER_GET_FISCAL_XML,
                                                     FM_PARAM,
                                                     str(order_id))
            if msg.token != TK_SYS_ACK:
                raise OrderError(remote_order_id, 5, "Error getting fiscal XML: {}".format(msg.data))
            fiscal_xml = msg.data

            def inner_func(conn):
                query = """
                INSERT OR REPLACE INTO ProducedOrders VALUES ('{}', '{}', '{}', 0)
                """.format(order_id, remote_order_id, fiscal_xml)
                conn.query(query)

            self.execute_with_connection(inner_func, service_name=SERVICE_NAME)
        except Exception as _:
            logger.exception('Error inserting produced order. OrderId#{}'.format(order_id))
            raise

    def pick_pending_order(self):
        def inner_func(conn):
            orders_to_produce = []
            
            query = """
            SELECT OrderId, RemoteOrderId, FiscalXml
            FROM ProducedOrders
            WHERE SentToSAC = 0
            """
            for row in conn.select(query):
                orders_to_produce.append((row.get_entry("OrderId"),
                                          row.get_entry("RemoteOrderId"),
                                          row.get_entry("FiscalXml")))
                
            return orders_to_produce
        return self.execute_with_connection(inner_func, service_name=SERVICE_NAME)

    def mark_order_as_sent(self, order_id='', remote_order_id=''):
        def inner_func(conn):
            query = """
            UPDATE ProducedOrders
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
        return self.execute_with_connection(inner_func, db_name=self.pos_id)

    def get_store_id(self, remote_order_id):
        def inner_func(conn):
            query = """
                select value
                from ordercustomproperties
                where orderid = (select orderid 
                                 from ordercustomproperties 
                                 where key = 'REMOTE_ORDER_ID' 
                                 and value = '{}')
                and key = 'ORIGINATOR'
            """.format(remote_order_id)
            for row in conn.select(query):
                return row.get_entry(0)
        return self.execute_with_connection(inner_func, db_name=self.pos_id)
