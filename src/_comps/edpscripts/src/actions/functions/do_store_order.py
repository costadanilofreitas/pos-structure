# -*- coding: utf-8 -*-
import sysactions
import logging
from mw_helper import show_message_dialog
from posot import OrderTakerException
from custom_sysactions import user_authorized_to_execute_action
from actions.fiscal.get_nf_type import get_nf_type
from actions.util import is_delivery_order
from actions.delivery.save_delivery_order import save_delivery_order

logger = logging.getLogger("PosActions")


@sysactions.action
@user_authorized_to_execute_action
def doStoreOrder(pos_id, totalize="none", show_popup=True, *args):
    from posactions import list_open_options, doTotal, fill_customer_properties, customer_info_config
    model = sysactions.get_model(pos_id)
    sysactions.check_current_order(pos_id, model=model, need_order=True)

    pos_ot = sysactions.get_posot(model)
    xml_order = sysactions.get_current_order(model)

    if float(xml_order.get("totalTender")) != 0:
        show_message_dialog(pos_id, "$ERROR", "$ORDER_HAS_TENDERS_CANNOT_SAVE")
        return

    if sysactions.get_current_order(model).get("type") != "SALE":
        sysactions.show_messagebox(pos_id, message="$THIS_ORDER_TYPE_CANNOT_BE_STORED", icon="warning")
        return

    order = model.find("CurrentOrder/Order")
    sale_lines = order.findall("SaleLine")
    deleted_line_numbers = map(lambda x: x.get("lineNumber"), filter(lambda x: x.get("level") == "0" and x.get("qty") == "0", sale_lines))
    active_sale_lines = filter(lambda x: x.get("lineNumber") not in deleted_line_numbers, sale_lines)

    if not active_sale_lines:
        sysactions.show_messagebox(pos_id, "$HAS_NO_ITEMS_IN_ORDER", title="")
        return

    option = list_open_options(order)
    if option is not None:
        prod_name = sysactions.get_line_product_name(model, int(option.get("lineNumber")))
        show_message_dialog(pos_id, "$ERROR", "$NEED_TO_RESOLVE_OPTION|%s" % (prod_name.encode("UTF-8")))
        return

    pod_function = sysactions.get_posfunction(model) if sysactions.get_podtype(model) in ("DT", "FC") else sysactions.get_podtype(model)
    if totalize == "none" and pod_function == "OT":
        totalize = "true"

    if get_nf_type(pos_id) == "PAF" and not pod_function == "OT":
        sysactions.show_messagebox(pos_id, message="$THIS_ORDER_TYPE_CANNOT_BE_STORED", icon="warning")
        return

    if (totalize.lower() != "true" or pod_function == "OT") and customer_info_config is not None:
        customer_document_config = customer_info_config[int(pos_id)]['document']
        customer_name_config = customer_info_config[int(pos_id)]['name']
        request_customer_info = "onSave" in customer_document_config or "onSave" in customer_name_config
        if request_customer_info:
            get_document = "onSave" in customer_document_config
            get_name = "onSave" in customer_name_config
            fill_customer_properties(model, pod_function, pos_id, pos_ot, get_doc=get_document, get_name=get_name)

    if totalize.lower() == "true":
        if doTotal(pos_id, screen_number="") == "Error":
            return

    # Pre-venda
    pre_venda = None
    if pod_function == "OT":
        for prop in order.findall("CustomOrderProperties/OrderProperty"):
            key, value = prop.get("key"), prop.get("value")
            if key == "PRE_VENDA":
                pre_venda = value
                break
    try:
        pos_ot.storeOrder(pos_id)

        if pre_venda:
            sysactions.show_messagebox(pos_id, "Pre Venda: PV%010d" % int(pre_venda))
        elif _save_order_on_remote_order(order, pos_id, pos_ot):
            if show_popup:
                sysactions.show_messagebox(pos_id, "$ORDER_SAVED")
        else:
            sysactions.show_messagebox(pos_id, "$ERROR_SAVING_ORDER")
    except OrderTakerException as ex:
        sysactions.show_messagebox(pos_id, message="$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()))

    order = model.find("CurrentOrder/Order")
    order_id = order.get("orderId")
    logger.debug("Pedido Salvo - Order %s - PosId %s" % (order_id, pos_id))


def _save_order_on_remote_order(order, pos_id, pos_ot):
    model = sysactions.get_model(pos_id)
    if is_delivery_order(model):
        order_id = order.get("orderId")
        
        try:
            save_delivery_order(order_id)
        except Exception as _:
            session = sysactions.get_operator_session(model)
            pos_ot.recallOrder(int(pos_id), int(order_id), session)
            return False
        
    return True

