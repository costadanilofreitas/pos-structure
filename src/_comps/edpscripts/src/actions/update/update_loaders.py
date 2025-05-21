# -*- coding: utf-8 -*-

from sysactions import action, show_messagebox
from bustoken import TK_POS_UPDATER_PERFORM_LOADER_UPDATE
from msgbus import TK_SYS_NAK

from .. import mb_context


@action
def update_loaders(pos_id):
    restart_hv = "false"
    response = show_messagebox(pos_id, "$RESTART_AFTER_UPDATE", buttons="$YES|$NO")
    if response == 0:
        restart_hv = "true"
    
    timeout = 60000000 * 5
    loader_update_token = TK_POS_UPDATER_PERFORM_LOADER_UPDATE
    msg = mb_context.MB_EasySendMessage("PosUpdater", loader_update_token, data=restart_hv, timeout=timeout)
    if msg.token == TK_SYS_NAK:
        show_messagebox(pos_id, "$UPDATE_LOADERS_" + msg.data.upper(), buttons="OK")
        return

    show_messagebox(pos_id, "$UPDATE_LOADERS_MESSAGE", buttons="OK")
