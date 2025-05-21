# -*- coding: utf-8 -*-
import json
import logging
import time

import sysactions
from msgbus import MBException
from sitef import SitefProcessor
from systools import sys_log_exception

logger = logging.getLogger("Sitef")


class MobileSitefProcessor(SitefProcessor):
    def __init__(self, mbcontext):
        super(MobileSitefProcessor, self).__init__()
        sysactions.mbcontext = mbcontext
        self.sitef_service_finder = MobileSitefServiceFinder()

    def process(self, bus_msg, pos_id, order_id, operador, tender_type, amount, data_fiscal, hora_fiscal, tender_seq_id, display_via_api=False, ip_sitef=None):
        return False, "Mobile Sitef cannot process transactions"

    def finalizar(self, pos_id, order_id, data_fiscal, hora_fiscal, status):
        transaction_data = {
            "timeStamp": time.time(),
            "confirmTransaction": status,
            "transactionIdentifier": str(pos_id) + str(order_id),
            "fiscalDate": data_fiscal,
            "fiscalTime": hora_fiscal
        }

        data = json.dumps(transaction_data)
        retry = 0
        while retry < 3:
            try:
                event_xml = """<Event subject="POS{}" type="MOBILE">
                                   <MOBILE_CONFIRM_TRANSACTION>
                                       {}
                                   </MOBILE_CONFIRM_TRANSACTION>
                               </Event>""".format(pos_id, data)

                sysactions.mbcontext.MB_EasyEvtSend("POS{}".format(int(pos_id)), "MOBILE", event_xml)
            except MBException as _:
                sys_log_exception("Error sending mobile confirm transaction")
            finally:
                retry += 1

    def cancel(self):
        raise Exception()

    def terminate(self):
        pass


class MobileSitefServiceFinder(object):
    def __init__(self):
        pass

    def lock_sitef(self):
        pass

    def release_sitef(self):
        pass
