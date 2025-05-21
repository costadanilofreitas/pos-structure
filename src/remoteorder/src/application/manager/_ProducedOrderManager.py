# -*- coding: utf-8 -*-

import json
import logging
import time
from threading import Thread

from msgbus import MBEasyContext

from application.model import DispatchedEvents, OrderProducedRequest, RemoteOrderModelJsonEncoder
from application.util import get_encoded_json
from application.repository import ProducedOrderRepository
from application.services import ProcessedOrderBuilder

logger = logging.getLogger("ProducedOrdersManager")


class ProducedOrderManager:

    def __init__(self, pos_id, mb_context, interval_to_send, produced_order_repository, processed_order_builder):
        # type: (int, MBEasyContext, int, ProducedOrderRepository, ProcessedOrderBuilder) -> None

        self.pos_id = pos_id
        self.interval_to_send = interval_to_send
        self.produced_order_repository = produced_order_repository
        self.processed_order_builder = processed_order_builder

        self.event_dispatcher = DispatchedEvents(mb_context)

        if interval_to_send > 0:
            sac_sync_thread = Thread(target=self._send_produced_order_data_to_sac, name="SAC Sync")
            sac_sync_thread.daemon = True
            sac_sync_thread.start()

    def _send_produced_order_data_to_sac(self):
        # type: () -> None

        while True:
            try:
                orders_to_produce = self.produced_order_repository.pick_pending_order()
                for order in orders_to_produce:
                    order_id = ''
                    try:
                        order_id, remote_id, fiscal_xml = order
                        store_id = self.produced_order_repository.get_store_id(remote_id)
                        if remote_id is not None:
                            logger.debug('Pending produced order found, dispatching event to SAC')
                            logger.debug('RemoteOrderId: {}; FiscalXML: {}'.format(remote_id, fiscal_xml))

                            processed_order = self.processed_order_builder.build_processed_order(remote_id, order_id, None)
                            items = get_encoded_json(processed_order.items)
                            data = OrderProducedRequest(remote_id, store_id, fiscal_xml, items, True)
                            json_data = json.dumps(data, encoding="utf-8", cls=RemoteOrderModelJsonEncoder)

                            self.event_dispatcher.send_event(DispatchedEvents.PosOrderProduced, "", json_data, logger)
                    except Exception as _:
                        logger.exception("Error sending produced order to SAC for order: {}".format(order_id))
            except Exception as _:
                logger.exception("Error processing orders to produce")
            finally:
                time.sleep(self.interval_to_send)
