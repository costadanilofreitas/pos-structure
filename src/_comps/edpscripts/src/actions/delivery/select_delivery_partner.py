# coding=utf-8
import json
import os
import cfgtools
import sysactions
from msgbus import TK_SYS_ACK
from sysactions import action, show_listbox, translate_message, StopAction, show_messagebox, show_keyboard, get_model
from bustoken import TK_REMOTE_ORDER_GET_LOGISTIC_PARTNERS, TK_REMOTE_ORDER_SEARCH_LOGISTIC

from .. import logger, mb_context
from model.customexception import LogisticPartnerNotFound, LogisticSearchError

logistic_partners = {}


@action
def select_logistic_partner(pos_id, order_id):
    # type: (str, str) -> None

    select_partner = _ask_for_logistic_partner(pos_id)
    if select_partner:
        _search_logistic_partner(order_id, pos_id, select_partner)


def _search_logistic_partner(order_id, pos_id, select_partner):
    params = [select_partner, order_id]

    if _should_ask_for_deliveryman_name():
        if select_partner == 'default':
            deliveryman_data = sysactions.show_keyboard(pos_id, "Nome do entregador")
            if deliveryman_data is not None and deliveryman_data != "":
                params.append(deliveryman_data)
            else:
                return

    data = json.dumps("\0".join(params))
    msg = mb_context.MB_EasySendMessage("RemoteOrder", TK_REMOTE_ORDER_SEARCH_LOGISTIC, data=data, timeout=10000000)
    if msg.token == TK_SYS_ACK:
        show_messagebox(pos_id, "$SEARCHING_LOGISTIC_PARTNER")
    else:
        raise LogisticSearchError()


def _ask_for_logistic_partner(pos_id):
    model = get_model(pos_id)
    partners = _get_logistic_partners(model)
    listbox_options = partners.values()
    index = show_listbox(pos_id, listbox_options, message="$DELIVERYMEN")
    if index is None:
        raise StopAction()
    
    select_partner = partners.keys()[partners.values().index(listbox_options[index])]
    return select_partner


def _get_logistic_partners(model):
    global logistic_partners
    
    if not logistic_partners:
        logger.debug("Getting Logistic Partners from Remote Order")
        msg = mb_context.MB_EasySendMessage("RemoteOrder", TK_REMOTE_ORDER_GET_LOGISTIC_PARTNERS, timeout=10000000)
        if msg.token == TK_SYS_ACK:
            logger.debug("Logistic Partners from Remote Order: {}".format(msg.data))
            partners = json.loads(msg.data)
            for partner in partners:
                partner_i18n = str("LOGISTIC_PARTNER_" + partner.upper())
                logistic_partners[partner] = translate_message(model, partner_i18n)
        else:
            logger.debug("Error getting Logistic Partners from Remote Order")
                
    if not logistic_partners:
        raise LogisticPartnerNotFound()
    
    return logistic_partners


def _should_ask_for_deliveryman_name():
    config = cfgtools.read(os.environ["LOADERCFG"])
    value = config.find_value("Customizations.DeliveryConfigurations.AskForDeliveryManName", False)
    value = str(value).upper() == 'TRUE'
    return value
