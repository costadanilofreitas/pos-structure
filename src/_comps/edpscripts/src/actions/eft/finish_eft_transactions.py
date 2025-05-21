import logging
import time

from bustoken import TK_SITEF_FINISH_PAYMENT
from msgbus import FM_PARAM, TK_SYS_ACK
from sysactions import mbcontext
from systools import sys_log_error

logger = logging.getLogger("TableActions")


def finish_eft_transactions(pos_id, order, status):
    order_tenders = order.findall(".//Tender")
    if len(order_tenders) == 0:
      return

    sitef_comp_name = "Sitef%02d" % int(pos_id)

    last_totaled = order \
        .findall("StateHistory/State[@state='TOTALED']")[-1] \
        .get("timestamp") \
        .replace("-", "") \
        .replace(":", "")

    order_id = order.get("orderId")
    data_fiscal = last_totaled[:8]
    hora_fiscal = last_totaled[9:15]
    data = ";".join([str(pos_id), order_id, data_fiscal, hora_fiscal, status])

    for try_num in range(1, 4):
        try:
            logger.info("[finish_eft_transactions] Trying to send a finish message. Order #: {}; Try #: {}; STATUS #: {}"
                        .format(order_id, try_num, status))
            ret = mbcontext.MB_EasySendMessage(sitef_comp_name, TK_SITEF_FINISH_PAYMENT, FM_PARAM, data)
            if ret.token == TK_SYS_ACK:
                logger.info("[finish_eft_transactions] Success finished eft transaction. Order #: {}".format(order_id))
                return
            else:
                logger.info("[finish_eft_transactions] ACK not received. Order #: {} - {} - {}".format(order_id,
                                                                                                       ret.token,
                                                                                                       ret.data))
            time.sleep(1)
        except Exception as _:
            msg = "[finish_eft_transactions] Error sending TK_SITEF_FINISH_PAYMENT message. Order #: {}; Try #: {}"\
                .format(order_id, try_num)
            logger.error(msg)
            sys_log_error(msg)
