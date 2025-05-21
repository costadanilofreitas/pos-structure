import datetime
import time

import sysactions
from actions.void.utils import void_order
from posot import OrderTakerException


def do_recall_order(pos_id, order_id, originator_pos_id=None, check_date=True, pos_ot=None):
    model = sysactions.get_model(pos_id)
    if pos_ot is None:
        pos_ot = sysactions.get_posot(model)
    session = sysactions.get_operator_session(model)

    if originator_pos_id:
        recall_pos = int(originator_pos_id[4:])
        try:
            pos_ot.recallOrder(int(pos_id), int(order_id), session, sourceposid=str(recall_pos))
        except OrderTakerException as _:
            pos_ot.recallOrder(int(pos_id), int(order_id), session)
    else:
        pos_ot.recallOrder(int(pos_id), int(order_id), session)

    if check_date is True:
        # Waits a maximum of 5 seconds for the order to "arrive" at the POS model
        time_limit = (time.time() + 5.0)
        while (time.time() < time_limit) and (not sysactions.has_current_order(sysactions.get_model(pos_id))):
            time.sleep(0.1)

        model = sysactions.get_model(pos_id)
        order = model.find("CurrentOrder/Order")

        # Cannot recall order older than 20 hours
        now = datetime.datetime.now()
        order_created_date = datetime.datetime.strptime(order.get("createdAt"), "%Y-%m-%dT%H:%M:%S.%f")
        if order_created_date < now - datetime.timedelta(hours=20):
            sysactions.show_messagebox(pos_id, "$CANNOT_RECALL_ORDER_TOO_OLD", title="$ERROR", icon="error")
            void_order(pos_id, void_reason=6, pos_ot=pos_ot)
            return
