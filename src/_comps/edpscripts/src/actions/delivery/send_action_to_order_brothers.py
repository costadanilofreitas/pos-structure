import json

from bustoken import TK_REMOTE_ORDER_GET_STORED_ORDERS
from msgbus import TK_SYS_ACK

from .. import mb_context


def send_action_to_order_brothers(pos_id, action, remote_id, execute=True, params=''):
    if not execute:
        return

    msg = mb_context.MB_EasySendMessage("RemoteOrder", TK_REMOTE_ORDER_GET_STORED_ORDERS)
    if msg.token != TK_SYS_ACK:
        return

    if msg.data:
        orders = []
        for order in json.loads(msg.data):
            order_remote_id = order.get("remoteId")
            father_remote_id = order.get("customProps").get("FATHER_REMOTE_ID")
            if father_remote_id and father_remote_id == remote_id and order_remote_id != remote_id:
                orders.append(order)
            
        for order in orders:
            if action == 'confirm_delivery_payment':
                import confirm_delivery_payment
                confirm_delivery_payment.confirm_delivery_payment(pos_id, order['Id'], order['remoteId'], False, params)
