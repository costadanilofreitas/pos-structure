# -*- coding: utf-8 -*-
import sysactions
from actions.login.utils import login_user


@sysactions.action
def unpause_user(pos_id, user_id):
    return login_user(pos_id, user_id)
