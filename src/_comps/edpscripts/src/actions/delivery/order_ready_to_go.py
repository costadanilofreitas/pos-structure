# -*- coding: utf-8 -*-

import sysactions

from systools import sys_log_exception


from .. import logger

from .. import mb_context


@sysactions.action
def order_ready_to_go(pos_id, order_id, external_id):
    try:
        xml = "|".join([order_id, external_id])
        mb_context.MB_EasyEvtSend("OrderReadyToGo", type="", xml=xml, sourceid=int(pos_id))

    except Exception as e:
        sys_log_exception("Error OrderReadyToGo")
        logger.error(e)
        return False
