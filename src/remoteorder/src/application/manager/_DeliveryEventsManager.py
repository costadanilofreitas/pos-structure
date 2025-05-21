# -*- coding: utf-8 -*-

import logging
import time

from threading import Thread

from application.model import DispatchedEvents, DeliveryEventTypes
from application.repository import DeliveryEventsRepository
from msgbus import MBEasyContext

logger = logging.getLogger("DeliveryEventsManager")


class DeliveryEventsManager(object):
    def __init__(self, pos_id, mb_context, interval_to_send, delivery_events_repository):
        # type: (int, MBEasyContext, int, DeliveryEventsRepository) -> None

        self.pos_id = pos_id
        self.interval_to_send = interval_to_send
        self.delivery_events_repository = delivery_events_repository

        self.event_dispatcher = DispatchedEvents(mb_context)

        if interval_to_send > 0:
            sac_sync_thread = Thread(target=self._send_delivery_events_to_server, name="Delivery Server Sync")
            sac_sync_thread.daemon = True
            sac_sync_thread.start()

    def _send_delivery_events_to_server(self):
        # type: () -> None

        while True:
            try:
                delivery_events = list(map(int, DeliveryEventTypes))
                for delivery_event in delivery_events:
                    events = self.delivery_events_repository.get_pending_delivery_events(delivery_event)
                    for event in events:
                        event_to_dispatch = self._get_event_to_dispatch(delivery_event)
                        if not event_to_dispatch:
                            continue

                        self.event_dispatcher.send_event(event_to_dispatch, "", event.event_data, logger)

            except Exception as _:
                logger.exception("Error sending event to Delivery Server")
            finally:
                time.sleep(self.interval_to_send * 60)

    @staticmethod
    def _get_event_to_dispatch(delivery_event):
        # type: (int) -> DispatchedEvents

        event_to_dispatch = ""
        if delivery_event == DeliveryEventTypes.ORDER_READY_TO_DELIVERY:
            event_to_dispatch = DispatchedEvents.PosOrderReadyToDelivery
        if delivery_event == DeliveryEventTypes.LOGISTIC_DISPATCHED:
            event_to_dispatch = DispatchedEvents.PosLogisticDispatched
        if delivery_event == DeliveryEventTypes.LOGISTIC_DELIVERED:
            event_to_dispatch = DispatchedEvents.PosLogisticDelivered

        return event_to_dispatch
