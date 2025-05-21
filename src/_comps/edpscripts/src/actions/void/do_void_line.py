import sysactions
from custom_sysactions import user_authorized_to_execute_action


@sysactions.action
@user_authorized_to_execute_action
def do_void_lines(pos_id, line_numbers=None, auth_data=None):
    if not line_numbers:
        return False

    model = sysactions.get_model(pos_id)
    sysactions.check_current_order(pos_id, model=model)

    if not sysactions.can_void_line(model, line_numbers):
        sysactions.show_messagebox(pos_id, "$NEED_TO_HAVE_ITEM_TO_VOID")
        return False

    pos_ot = sysactions.get_posot(model)
    order = model.find("CurrentOrder/Order")
    order_id = order.get("orderId")
    sale_lines = order.findall("SaleLine")

    pos_ot.voidLine(int(pos_id), line_numbers)
    if not auth_data:
        return True

    for line_number in line_numbers.split('|'):
        deleted_line = filter(lambda x: x.get("lineNumber") == line_number and x.get("level") == "0", sale_lines)[0]
        part_code = deleted_line.get("partCode")
        item_id = deleted_line.get("itemId")
        pos_ot.setOrderCustomProperty("VoidAuthUser", auth_data[0], order_id, line_number, item_id, '0', part_code)

    return True
