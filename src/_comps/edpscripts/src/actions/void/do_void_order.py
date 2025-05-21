import base64
from datetime import datetime, timedelta
from old_helper import convert_from_utf_to_localtime

import sysactions
from custom_sysactions import user_authorized_to_execute_action
from utils import get_void_reason_id, void_order, void_fiscal_order
from .. import logger


@sysactions.action
@user_authorized_to_execute_action
def do_void_order(pos_id, void_reason=None, fiscal_void='false', order_id="", show_cancel_message=True):
    try:
        model = sysactions.get_model(pos_id)
        originator_pos_id = pos_id
        
        if fiscal_void.lower() == 'true':
            order_id, originator_pos_id = _void_fiscal_order(pos_id, model)
        else:
            sysactions.check_current_order(pos_id, model)
    
        void_reason = get_void_reason_id(pos_id, void_reason)
        if not void_reason:
            return True
    
        void_order(originator_pos_id, order_id=order_id, void_reason=void_reason)
    
        if show_cancel_message:
            sysactions.show_messagebox(pos_id, "$ORDER_VOIDED_WITH_SUCCESS")
    
        return True
    except BaseException as _:
        logger.exception("Error voiding order {}".format(str(order_id) if order_id else 'undefined'))
        if show_cancel_message:
            sysactions.show_messagebox(pos_id, "$ERROR_CANCEL_ORDER")
            
        return False


def _void_fiscal_order(pos_id, model):
    order_id = ""
    posot = sysactions.get_posot(model)
    limit_datetime = datetime.now() - timedelta(minutes=30)
    orders = posot.listOrders(state="PAID", since=limit_datetime.strftime("%Y-%m-%dT%H:%M:%S"))
    order_options = []
    baseurl = "/mwapp/services/PosController/POS{}/?token=TK_POS_EXECUTEACTION&format=2&isBase64=true&payload=" \
        .format(pos_id)
    order_descr = "{} - {} POS{:02} - {:05} - R${:.2f}"
    for order in orders:
        if 'custom_properties' in order and 'FISCALIZATION_DATE' in order['custom_properties']:
            fiscalization_prop = order['custom_properties']['FISCALIZATION_DATE']
            fiscalization_date = convert_from_utf_to_localtime(datetime.strptime(fiscalization_prop, "%Y-%m-%dT%H:%M:%S"))
            if fiscalization_date.replace(tzinfo=None) > limit_datetime:
                descr = order_descr.format(
                    fiscalization_date.strftime('%H:%M'),
                    order['podType'],
                    int(order['originatorId'][3:]),
                    int(order['orderId']),
                    float(order['totalGross'])
                )
                payload = base64.b64encode("\0".join(("doOrderPicture", pos_id, order['orderId'])))
                url = baseurl + payload
                order_options.append((order['orderId'], descr, url))
    if len(order_options) > 0:
        selected = sysactions.show_order_preview(pos_id,
                                                 order_options,
                                                 "$SELECT_AN_ORDER_TO_CANCEL",
                                                 buttons="CANCEL|OK",
                                                 onthefly=True)
        if (selected is None) or (selected[0] == "0"):
            raise sysactions.StopAction()
        order_id = selected[1]
    if order_id:
        originator_pos_id = int(next(iter([x for x in orders if x['orderId'] == order_id]))['originatorId'][3:])
        void_fiscal_order(originator_pos_id, order_id)
    else:
        sysactions.show_messagebox(pos_id, "$NO_ORDER_FOUND_TO_CANCEL")
        raise sysactions.StopAction()
    return order_id, originator_pos_id
