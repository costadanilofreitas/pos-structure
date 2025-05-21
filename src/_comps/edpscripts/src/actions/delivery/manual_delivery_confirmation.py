# -*- coding: utf-8 -*-

import sysactions
from systools import sys_log_exception

from .. import logger
from .. import mb_context


@sysactions.action
def manual_delivery_confirmation(pos_id, order_id):
    try:        
        mb_context.MB_EasyEvtSend("ManualConfirmDeliveryOrder", type="", xml=order_id, sourceid=int(pos_id))

    except Exception as e:
        sys_log_exception("Error ManualConfirmDeliveryOrder")
        logger.error(e)
        return False
