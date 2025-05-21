# -*- coding: utf-8 -*-
import sysactions


@sysactions.action
def process_external_payments(pos_id, options, amount, is_table_service, selected_seats='', device_type=''):
    from posactions import get_tender_types, doTender
    from table_actions import do_table_tender

    is_table_service = str(is_table_service).lower() == "true"
    tender_types = get_tender_types()
    options = options.split(',')
    tender_types = [tender for tender in tender_types if str(tender["id"]) in options]
    options = [tender["descr"] for tender in tender_types]
    selected_option = sysactions.show_listbox(pos_id, options)
    if selected_option is None:
        return

    selected_tender = tender_types[selected_option]
    if is_table_service:
        return do_table_tender(pos_id, selected_tender["id"], amount, None, None, selected_seats, device_type)
    else:
        return doTender(pos_id, amount, selected_tender["id"], "false", "true")
