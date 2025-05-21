# -*- coding: utf-8 -*-

import sysactions

from bustoken import TK_POS_UPDATER_PERFORM_USER_UPDATE
from msgbus import TK_SYS_NAK, FM_PARAM


@sysactions.action
def update_users(pos_id):
    msg = sysactions.send_message("PosUpdater", TK_POS_UPDATER_PERFORM_USER_UPDATE, FM_PARAM)
    if msg.token == TK_SYS_NAK:
        sysactions.show_messagebox(pos_id, "$UPDATE_USERS_" + msg.data.upper(), buttons="OK")
        return

    sysactions.show_messagebox(pos_id, "$UPDATE_USERS_MESSAGE", buttons="OK")
