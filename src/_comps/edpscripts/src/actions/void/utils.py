# -*- coding: utf-8 -*-
import sysactions
from bustoken import TK_FISCALWRAPPER_CANCEL_ORDER
from msgbus import FM_PARAM, TK_SYS_ACK
from mw_helper import show_filtered_list_box_dialog

from .. import mb_context


def void_order(pos_id, last_paid_order="0", order_id='', abandon=0, void_reason=9, pos_ot=None):
    model = sysactions.get_model(pos_id)
    if pos_ot is None:
        pos_ot = sysactions.get_posot(model)

    order_id = int(order_id) if order_id != "" else ""
    pos_ot.voidOrder(int(pos_id), int(last_paid_order), order_id, abandon)
    if (type(void_reason) == int) or not void_reason:
        void_reason = get_void_reason_id(pos_id, void_reason)
    if not order_id:
        order = sysactions.get_current_order(model)
        order_id = order.get('orderId')
    pos_ot.setOrderCustomProperties(void_reason, str(order_id))

    return True


def void_fiscal_order(pos_id, order_id):
    data = "|".join([str(pos_id), str(order_id)])
    msg = mb_context.MB_EasySendMessage("FiscalWrapper", TK_FISCALWRAPPER_CANCEL_ORDER, format=FM_PARAM, data=data)
    if not msg.token == TK_SYS_ACK:
        sysactions.show_messagebox(pos_id, message="$ERROR_CANCEL_FISCAL_ORDER|{}".format(msg.data))
        raise sysactions.StopAction(msg.data)


def get_void_reason_id(pos_id, selected_index=None):
    void_reason_ids = range(1, 13)
    void_reason_options = ["1 - Mudou de Ideia",
                           "2 - Duplicado",
                           "3 - Venda Errada",
                           "4 - Cancelamento",
                           "5 - Cupom Cancelado",
                           "6 - Pagamento Cancelado",
                           "7 - Pedido Salvo Cancelado",
                           "8 - Erro ao criar nova venda",
                           "9 - Erro ao processar pagamento",
                           "10 - Cancelamento via sistema",
                           "11 - Erro de sincronização",
                           "12 - Cancelamento com autorização do gerente"]
    void_reason_to_show = void_reason_options[0:4]
    if not selected_index:
        message = "Selecione o Motivo:"
        selected_index = show_filtered_list_box_dialog(pos_id, void_reason_to_show, message, mask="NOFILTER")

    if selected_index is None:
        return None

    void_reason_id = void_reason_ids[int(selected_index)]
    void_reason_descr = void_reason_options[int(selected_index)]
    void_reason_dict = {'VOID_REASON_ID': void_reason_id, 'VOID_REASON_DESCR': void_reason_descr}

    return void_reason_dict
