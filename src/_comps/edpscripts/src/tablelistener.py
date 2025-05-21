# -*- coding: utf-8 -*-

import logging
from xml.etree import cElementTree as eTree

import pyscripts
import sysactions

mbcontext = pyscripts.mbcontext

logger = logging.getLogger("PosActions")


class TableEvents(object):
    TOTALED       = "TABLE_TOTALED"
    STORED        = "TABLE_STORED"
    REOPENED      = "TABLE_REOPENED"
    CLOSED        = "TABLE_CLOSED"
    READY4SERVICE = "TABLE_READY4SERVICE"


def main():
    _load_pos_configs()

    pyscripts.subscribe_event_listener(TableEvents.TOTALED, _event_table_modifier_handler)
    pyscripts.subscribe_event_listener(TableEvents.STORED, _event_table_modifier_handler)
    pyscripts.subscribe_event_listener(TableEvents.REOPENED, _event_table_modifier_handler)
    pyscripts.subscribe_event_listener(TableEvents.CLOSED, _event_table_modifier_handler)
    pyscripts.subscribe_event_listener(TableEvents.READY4SERVICE, _event_table_modifier_handler)


def _load_pos_configs():
    global auto_print_table_report_cfg

    auto_print_table_report = sysactions.get_storewide_config("Store.AutoPrintTableReport")
    auto_print_table_report_cfg = auto_print_table_report.split("\0") if auto_print_table_report else []


def _event_table_modifier_handler(params):
    event_xml = params[0]
    subject = params[1]
    pos_id = params[4]

    try:
        table_id = eTree.XML(event_xml).find(".//Table").get("id")

        if subject == TableEvents.TOTALED:
            _table_totaled_event(pos_id, table_id)
        elif subject == TableEvents.STORED:
            _table_stored_event(pos_id, table_id)
        elif subject == TableEvents.REOPENED:
            _table_reopened_event(pos_id, table_id)
        elif subject == TableEvents.CLOSED:
            _table_closed_event(pos_id, table_id)
        elif subject == TableEvents.READY4SERVICE:
            _table_ready4service_event(pos_id, table_id)
        else:
            logger.info("[tablelistener] Untreated subject received: {}".format(subject))
    except Exception as _:
        msg = "[tablelistener] Error treating subject: {}".format(subject)
        logger.exception(msg)
        sysactions.sys_log_exception(msg)


def _table_totaled_event(pos_id, table_id):
    _print_table_report(pos_id, table_id, TableEvents.TOTALED)


def _table_stored_event(pos_id, table_id):
    _print_table_report(pos_id, table_id, TableEvents.STORED)


def _table_reopened_event(pos_id, table_id):
    pass


def _table_closed_event(pos_id, table_id):
    pass


def _table_ready4service_event(pos_id, table_id):
    pass


def _print_table_report(pos_id, table_id, table_event):
    if table_event in auto_print_table_report_cfg:
        sysactions.print_report(pos_id, sysactions.get_model(pos_id), False, "table_report", pos_id, table_id)
