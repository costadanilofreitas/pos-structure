# -*- coding: utf-8 -*-

import sysactions

from bustoken import TK_POS_UPDATER_PERFORM_CATALOG_UPDATE, TK_POS_GET_CATALOG_VERSION_TO_APPLY
from msgbus import TK_SYS_NAK, FM_PARAM


@sysactions.action
def update_menu(pos_id):
    try:
        msg = sysactions.send_message("PosUpdater", TK_POS_GET_CATALOG_VERSION_TO_APPLY, FM_PARAM)
        if msg.token == TK_SYS_NAK:
            sysactions.show_messagebox(pos_id, "$UPDATE_MENU_" + msg.data.upper(), buttons="OK")
            return
    
        resp = sysactions.show_messagebox(pos_id, "$UPDATE_MENU_VERSION_AVAILABLE|" + msg.data, buttons="$OK|$CANCEL")
        if resp == 1:
            return
    
        resp = sysactions.show_messagebox(pos_id, "$UPDATE_MENU_MESSAGE", buttons="$OK|$CANCEL")
        if resp == 1:
            return
    
        msg = sysactions.send_message("PosUpdater", TK_POS_UPDATER_PERFORM_CATALOG_UPDATE, FM_PARAM)
        if msg.token == TK_SYS_NAK:
            sysactions.show_messagebox(pos_id, "$UPDATE_MENU_" + msg.data.upper(), "$INFORMATION", buttons="OK")
    except Exception as _:
        sysactions.sys_log_exception("Error updating menu")
        sysactions.show_messagebox(pos_id, "$UPDATE_MENU_EXCEPTION", "$INFORMATION", buttons="OK")
