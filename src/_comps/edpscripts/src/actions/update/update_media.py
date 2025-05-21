# -*- coding: utf-8 -*-

import sysactions

from bustoken import TK_POS_UPDATER_PERFORM_MEDIA_UPDATE
from msgbus import TK_SYS_NAK, FM_PARAM


@sysactions.action
def update_media(pos_id):
    msg = sysactions.send_message("PosUpdater", TK_POS_UPDATER_PERFORM_MEDIA_UPDATE, FM_PARAM)
    if msg.token == TK_SYS_NAK:
        if not msg.data:
            sysactions.show_messagebox(pos_id, "$UPDATE_MEDIA_DISABLED" + msg.data.upper(), buttons="OK")
        else:
            sysactions.show_messagebox(pos_id, "$UPDATE_MEDIA_" + msg.data.upper(), buttons="OK")
            
        return
    
    sysactions.show_messagebox(pos_id, "$UPDATE_MEDIA_MESSAGE", buttons="OK")