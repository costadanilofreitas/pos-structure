# -*- coding: utf-8 -*-
import sysactions
from sysactions import get_model

from login_user import loginuser
from signin_user import sign_in_table_user
from actions.pos import pos_must_be_blocked

SIGNED_IN_USER = "SIGNED_IN_USER"
USECS_PER_SEC = 1000000


@sysactions.action
def common_login(pos_id, user_id=None, password=None):
    if pos_must_be_blocked(pos_id):
        return False

    model = get_model(pos_id)
    working_mode = model.find("WorkingMode").get("usrCtrlType")

    if working_mode == "QSR":
        return loginuser(pos_id, user_id, password)
    else:
        return sign_in_table_user(pos_id, user_id)
