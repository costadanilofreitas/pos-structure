# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta

from sysactions import get_model, get_business_period, get_cfg, is_day_opened, has_current_order
from systools import sys_log_exception

pos_block_hour = {}
pos_datetime_to_block_pos = {}

logger = logging.getLogger("TableActions")


def pos_must_be_blocked(pos_id):
    try:
        model = get_model(pos_id)
        if has_current_order(model):
            return False

        if pos_id not in pos_block_hour:
            pos_block_hour[pos_id] = int(get_cfg(pos_id).key_value("hourToBlockPos", "0"))

        if pos_id in pos_datetime_to_block_pos:
            datetime_to_block_pos = pos_datetime_to_block_pos[pos_id]
        else:
            hour_to_block_pos = pos_block_hour[pos_id]
            period = get_business_period(model)

            if period == '0' or not is_day_opened(model):
                return False

            datetime_to_block_pos = datetime(int(period[:4]), int(period[4:6]), int(period[6:8]))
            datetime_to_block_pos += timedelta(days=1)
            datetime_to_block_pos += timedelta(hours=hour_to_block_pos)

        current_date = datetime.now()
        if current_date > datetime_to_block_pos:
            logger.debug(">>> PRE: pos_datetime_to_block_pos: {}".format(pos_datetime_to_block_pos))
            if pos_id in pos_datetime_to_block_pos:
                pos_datetime_to_block_pos.pop(pos_id, None)

            logger.debug(">>> POS: pos_datetime_to_block_pos: {}".format(pos_datetime_to_block_pos))
            return True
        else:
            pos_datetime_to_block_pos[pos_id] = datetime_to_block_pos
    except Exception as _:
        sys_log_exception("Error verifying if POS {} must be blocked".format(pos_id))

    return False
