# -*- coding: utf-8 -*-

import logging
import time

from msgbus import MBEasyContext
from persistence import Driver, AprDbdException, DbdException

logger = logging.getLogger("RemoteOrder")


class FiscalRepository(object):
    def __init__(self, mb_context):
        # type: (MBEasyContext) -> None
        self.mb_context = mb_context

    def add_payment_data(self, pos_id, order_id, tender_id, tender_type, amount, change):
        # type: (int, int, int, int, float, float) -> None
        retry = 1
        while retry <= 3:
            conn = None
            try:
                conn = Driver().open(self.mb_context, service_name="FiscalPersistence")
                conn.query("insert or replace into PaymentData (PosId, OrderId, TenderSeqId, Type, Amount, Change) VALUES ({0}, {1}, {2}, {3}, {4}, {5})"
                           .format(pos_id, order_id, tender_id, tender_type, amount, change))
                break
            except (AprDbdException, DbdException) as _:
                logger.exception("Error inserting fiscal payment on database. OrderId#{}. Try: {}/3"
                                 .format(order_id, retry))
                retry += 1
                time.sleep(1)
            finally:
                if conn:
                    conn.close()
