# -*- coding: utf-8 -*-

import sysactions
from systools import sys_log_exception


@sysactions.action
def do_void_kiosk_order(pos_id, show_message="false"):
    try:
        model = sysactions.get_model(pos_id)
        pos_ot = sysactions.get_posot(model)

        if sysactions.has_current_order(model):
            order = sysactions.get_current_order(model)
            if order.get("state") not in ["IN_PROGRESS", "TOTALED"]:
                return

            show_message = (show_message or "false").lower() == "true"
            if show_message and float(order.get("totalGross")) > 0:
                ret = sysactions.show_messagebox(pos_id, "$KIOSK_CANCEL_QUESTION", "$VOID_SALE", "$YES|$NO")
                if ret != 0:
                    raise sysactions.StopAction()

            pos_ot.voidOrder(pos_id)

        return True
    except BaseException as _:
        sys_log_exception("Error voiding kiosk order")
        return False
