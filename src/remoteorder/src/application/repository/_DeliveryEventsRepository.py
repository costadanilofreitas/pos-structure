# -*- coding: utf-8 -*-

import logging

from application.model import DeliveryEvent, DispatchedEvents, DeliveryEventTypes
from mwhelper import BaseRepository
from typing import List

logger = logging.getLogger("DeliveryEventsRepository")

SERVICE_NAME = "DeliveryPersistence"


class DeliveryEventsRepository(BaseRepository):
    def __init__(self, mb_context, pos_id, produced_order_repository):
        super(DeliveryEventsRepository, self).__init__(mb_context)
        self.pos_id = pos_id
        self.produced_order_repository = produced_order_repository

    def insert_delivery_event(self, order_id, remote_order_id, event_type, event_data):
        # type: (int, str, str, str) -> None

        try:
            def inner_func(conn):
                query = """
                INSERT OR REPLACE INTO DeliveryEvents 
                VALUES ({}, '{}', '{}', '{}', datetime('now'), 0)
                """.format(order_id, remote_order_id, event_type, event_data)
                conn.query(query)

            self.execute_with_transaction(inner_func, service_name=SERVICE_NAME)
        except Exception as _:
            logger.exception('Error inserting delivery event. OrderId: {}'.format(order_id))
            raise

    def set_event_server_ack(self, order_id, event_type):
        # type: (int, str) -> None

        try:
            def inner_func(conn):
                query = """
                            UPDATE DeliveryEvents 
                            SET ServerAck = 1
                            WHERE OrderId = {} AND EventType = '{}'
                        """.format(order_id, event_type)
                conn.query(query)

            self.execute_with_transaction(inner_func, service_name=SERVICE_NAME)
        except Exception as _:
            logger.exception('Error confirming delivery event. OrderId: {}'.format(order_id))
            raise

    def get_pending_delivery_events(self, selected_event_type):
        # type: (int) -> List[DeliveryEvent]

        def inner_func(conn):
            query = """
                        SELECT OrderId, RemoteOrderId, EventType, EventData
                        FROM DeliveryEvents
                        WHERE ServerAck = 0 AND EventType = '{}' AND InsertTime >= datetime('now', '-7 days')
                    """.format(selected_event_type)

            events = []

            for row in conn.select(query):
                order_id = row.get_entry("OrderId")
                remote_order_id = row.get_entry("RemoteOrderId")
                event_type = row.get_entry("EventType")
                event_data = row.get_entry("EventData")
                events.append(DeliveryEvent(order_id, remote_order_id, event_type, event_data))

            if selected_event_type == DeliveryEventTypes.ORDER_READY_TO_DELIVERY:
                fiscal_pending_orders = self.produced_order_repository.pick_pending_order()
                pending_order_ids = [x[0] for x in fiscal_pending_orders]
                events = [x for x in events if x.order_id not in pending_order_ids]

            return events

        return self.execute_with_connection(inner_func, service_name=SERVICE_NAME)
