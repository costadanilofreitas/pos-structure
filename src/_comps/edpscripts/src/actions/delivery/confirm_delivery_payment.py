import json
from datetime import datetime
from xml.etree import cElementTree as eTree

import sysactions
from mw_helper import show_confirm_dialog

import send_action_to_order_brothers
from .. import logger
from .. import mb_context


@sysactions.action
def confirm_delivery_payment(pos_id, order_id, external_id, execute_to_brothers=True):
    from posactions import ask_for_delivery_payment

    order_taker = None
    try:
        send_action_to_order_brothers.send_action_to_order_brothers(pos_id,
                                                                    'confirm_delivery_payment',
                                                                    external_id,
                                                                    execute_to_brothers)
        model = sysactions.get_model(pos_id)
        order_taker = sysactions.get_posot(model)
        message = "$CONFIRM_DELIVERY_PAYMENT"
        order_pict = order_taker.orderPicture(orderid=order_id)
        order = eTree.XML(order_pict).find("Order")
        order_state = order.attrib['state']
        tender_prepaid = order_taker.getOrderCustomProperties(key="PREPAID", orderid=order_id)
        tender_prepaid = eTree.XML(tender_prepaid).find("OrderProperty")
        if tender_prepaid is not None:
            tender_prepaid = tender_prepaid.get('value')
        else:
            tender_prepaid = 'true'

        if (tender_prepaid.lower() != 'true' and order_state != 'VOIDED') and ask_for_delivery_payment:
            tenders = show_confirm_dialog(pos_id, title=message)
            tenders = None if tenders is None else json.loads(tenders)
            if tenders is None:
                return False
            new_tenders = []
            for value in tenders:
                amount = float(value["amount"])
                tender_id = int(value["tenderId"])
                if amount != 0:
                    tender = {}
                    value = "{:.2f}".format(round(amount, 2))
                    tender['tenderid'] = tender_id
                    tender['amount'] = value
                    tender['tip'] = '0.00'
                    tender['tenderdetail'] = 'confirmDelivery'
                    new_tenders.append(tender)
            if not new_tenders:
                sysactions.show_messagebox(pos_id, "$NO_PAYMENT_DETECTED")
                return False
            for original_tender in order.findall('TenderHistory/Tender'):
                if original_tender.attrib['tenderType'] not in ("0", "201"):
                    tender = {}
                    value = "{:.2f}".format(round(float(original_tender.attrib['tenderAmount']), 2))
                    tender['tenderid'] = int(original_tender.attrib['tenderType'])
                    tender['amount'] = value
                    tender['tip'] = '0.00'
                    tender['tenderdetail'] = 'confirmDelivery'
                    new_tenders.append(tender)
            order_taker.blkopnotify = True
            order_pos_id = int(order.attrib["originatorId"][3:])
            model_delivery = sysactions.get_model(order_pos_id)
            order_taker_delivery = sysactions.get_posot(model_delivery)
            try:
                returned_tenders = order_taker_delivery.resetOrderTenders(order_id, new_tenders)
            except Exception, _ :
                sysactions.show_messagebox(pos_id, '$DELIVERY_CONFIRM_ERROR_NOT_PAID', title='', timeout=720000, buttons="$OK")
                return False
            logger.debug(returned_tenders)
            order_taker.blkopnotify = False
            if returned_tenders:
                total_amount = float(returned_tenders['totalAmount'])
                new_total_tender = float(returned_tenders['totalTender'])
                if new_total_tender > total_amount:
                    sysactions.show_messagebox(pos_id, returned_tenders['change'], title='$NEW_CHANGE', timeout=720000, buttons="$OK")
            else:
                return False
        else:
            confirmation = sysactions.show_messagebox(pos_id, message, title='', timeout=720000, buttons="$OK|$CANCEL")
            if confirmation == 1:
                return False

        xml = "|".join([order_id, external_id])
        mb_context.MB_EasyEvtSend("ConfirmDeliveryPayment", type="", xml=xml, sourceid=int(pos_id))
        time = datetime.now()
        order_taker.setOrderCustomProperties({'CONFIRM_DELIVERY_PAYMENT': True}, order_id)
        order_taker.setOrderCustomProperties({'CONFIRM_DELIVERY_PAYMENT_DATETIME': time}, order_id)

    except Exception as ex:
        sysactions.show_messagebox(pos_id, "$ERROR_ON_REMOTE_ORDER_DELIVERY_CONFIRMATION|{}".format(ex))
        logger.error(ex)
        return False
    finally:
        order_taker.blkopnotify = False

    return True
