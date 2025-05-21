import sysactions
from actions.void.utils import get_void_reason_id, void_order
from custom_sysactions import user_authorized_to_execute_action
from posot import OrderTakerException

@sysactions.action
def do_back_from_total(pos_id, void_reason=5, *args):
    model = sysactions.get_model(pos_id)
    pos_ot = sysactions.get_posot(model)
    order = model.find("CurrentOrder/Order")

    try:
        from table_actions import clean_discounts_and_payments
        clean_discounts_and_payments(pos_id, pos_ot, order)
        sysactions.check_current_order(pos_id, model=model)
        sysactions.get_posot(model).reopenOrder(int(pos_id))

    except OrderTakerException as ex:
        sysactions.show_messagebox(pos_id, message="$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()))


@user_authorized_to_execute_action
def void_order_with_payments(pos_id, void_reason):
    confirm = sysactions.show_confirmation(pos_id, "$CANNOT_CHANGE_ORDER_WITH_PAYMENTS", timeout=180000)
    if confirm:
        void_reason = get_void_reason_id(pos_id, void_reason)
        if not void_reason:
            raise sysactions.StopAction()

        void_order(pos_id, void_reason=void_reason)
