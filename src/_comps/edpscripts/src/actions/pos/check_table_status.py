# -*- coding: utf-8 -*-

from manager.reports import opened_tables_report
from sysactions import show_messagebox


def has_tab_or_tables_opened(period, pos_id):
    from msgbusboundary import MsgBusTableService as tableService

    for table in tableService().list_tables(pos_id):
        if not table.business_period == int(period):
            continue
        is_tab_opened = "TAB" in table.id and int(table.status) not in [1, 7]
        is_table_opened = "TAB" not in table.id and int(table.status) != 1
        if is_tab_opened or is_table_opened:
            ret = show_messagebox(pos_id, "$NEED_TO_CLOSE_ALL_TABLES_AND_TABS", buttons="$YES|$NO")
            if ret == 0:
                opened_tables_report(pos_id)
            return True
    return False
