# -*- coding: utf-8 -*-
import sysactions
from sysactions import get_model

from logoff_user import logoffuser
from signout_user import sign_out_user

SIGNED_IN_USER = "SIGNED_IN_USER"
USECS_PER_SEC = 1000000


@sysactions.action
def common_logoff(pos_id, user_id=None, password=None):
    model = get_model(pos_id)
    working_mode = model.find("WorkingMode").get("usrCtrlType")

    if working_mode == "QSR":
        return logoffuser(pos_id, user_id, password)
    else:
        return sign_out_user(pos_id, user_id)
