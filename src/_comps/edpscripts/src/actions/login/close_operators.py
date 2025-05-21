# -*- coding: utf-8 -*-
import sysactions
from actions.login.signout_user import sign_out_user
from xml.etree import cElementTree as etree

from actions.util.list_users import get_opened_users_from_pos
from ..util import get_selected_opened_user


@sysactions.action
def close_operators(pos_id):
    model = sysactions.get_model(pos_id)
    sysactions.check_current_order(pos_id, model=model, need_order=False)

    user, operator = get_opened_users_from_pos(pos_id)

    if user is None:
        return False

    return sign_out_user(pos_id, user.get("id"))
