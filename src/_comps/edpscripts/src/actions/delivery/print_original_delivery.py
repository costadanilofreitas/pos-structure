import bustoken
import sysactions

from msgbus import TK_SYS_ACK

from .. import mb_context
from model.customexception import DeliveryCouponPrintError

TK_REMOTE_ORDER_REPRINT_DELIVERY = bustoken.create_token(bustoken.MSGPRT_LOW, "37", "216")


@sysactions.action
def print_original_delivery(pos_id, order_id):
    data = pos_id + "\0" + order_id + "\0" + ','.join(str(x) for x in list(sysactions.get_poslist()))
    msg = mb_context.MB_EasySendMessage("RemoteOrder", TK_REMOTE_ORDER_REPRINT_DELIVERY, data=data, timeout=10000000)
    if msg.token == TK_SYS_ACK:
        return
    
    raise DeliveryCouponPrintError("Could not retrieve remote order status")
