# -*- coding: utf-8 -*-

from sysactions import action, show_any_dialog


@action
def delivery_address(pos_id):
    ret = show_any_dialog(pos_id, "deliveryAddress", "", "", "", "", "", 6000000, "", "", "", "", "", False)
    return ret
