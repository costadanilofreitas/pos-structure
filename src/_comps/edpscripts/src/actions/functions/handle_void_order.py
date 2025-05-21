import sysactions
from actions.kiosk import do_void_kiosk_order
from actions.void.do_void_order import do_void_order


@sysactions.action
def handle_void_order(pos_id, void_reason=None, fiscal_void="false", order_id="", show_cancel_message="true"):
    try:
        model = sysactions.get_model(pos_id)
        pod_type = sysactions.get_podtype(model)
        is_totem_order = pod_type == "TT"
        if is_totem_order:
            return do_void_kiosk_order(pos_id)
        return do_void_order(pos_id, void_reason, fiscal_void, order_id, show_cancel_message == "true")
    except BaseException as _:
        return False
