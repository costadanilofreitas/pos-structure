import logging

from sysactions import get_model, get_posot, has_current_order, get_current_order

logger = logging.getLogger("PosActions")


def check_active_order(pos_id, model=None):
    if model is None:
        model = get_model(pos_id)
    pos_ot = get_posot(model)
    if has_current_order(model):
        try:
            pos_ot.blkopnotify = True
            order = get_current_order(model)
            order_id = order.get("orderId")
            logger.info("POS has opened Order - Store and Proceed (Order Id: {})".format(order_id))
            pos_ot.storeOrder(pos_id)
        finally:
            pos_ot.blkopnotify = False
