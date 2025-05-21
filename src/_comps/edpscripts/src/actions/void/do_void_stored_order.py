import sysactions
from actions.functions.do_recall_order import do_recall_order
from systools import sys_log_exception
from utils import get_void_reason_id, void_order


@sysactions.action
def do_void_stored_order(pos_id, order_id="", orig_id="", void_reason=6, *args):
    try:
        void_reason = get_void_reason_id(pos_id, void_reason)
        if not void_reason:
            return

        do_recall_order(pos_id, order_id, check_date=False)
        void_order(pos_id, void_reason=void_reason)

        sysactions.show_messagebox(pos_id, "$STORED_ORDER_IS_VOIDED")
    except Exception as _:
        sysactions.show_messagebox(pos_id, "$ERROR_VOIDING_STORED_ORDER", "$ERROR")
        sys_log_exception("Erro ao apagar pedido salvo")
