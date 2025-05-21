# -*- coding: utf-8 -*-
import sysactions
from sysactions import check_operator_logged, StopAction

from msgbus import TK_POS_USERPAUSE, FM_PARAM, TK_SYS_ACK
from .. import logger


@sysactions.action
def pause_user(pos_id):
    try:
        check_operator_logged(pos_id)

        from table_actions import deselect_table
        deselect_table(pos_id)

        msg = sysactions.send_message(
            "POS{}".format(pos_id),
            TK_POS_USERPAUSE,
            FM_PARAM,
            pos_id,
            timeout=60 * 1000000
        )
        if msg.token != TK_SYS_ACK:
            error_code = msg.data.split('\0')[0]
            if error_code == "5003":  # POS BLOCKED BY TIME
                return True

            logger.error("Invalid response from PosCtrl while Pausing user: {} - {}".format(error_code, msg.data))
            sysactions.show_messagebox(pos_id, "$INVALID_USERNAME_OR_PASSWORD", "$INFORMATION")
            return False
    except StopAction:
        return False
    except (Exception, BaseException):
        logger.exception("Exception while pausing user on POS: {}".format(pos_id))
        sysactions.show_messagebox(pos_id, "$INVALID_USERNAME_OR_PASSWORD", "$INFORMATION")
        return False
    return True
