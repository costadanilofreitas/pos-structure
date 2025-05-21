# -*- coding: utf-8 -*-

import json
import os

import cfgtools
import sysactions
from actions import mb_context
from persistence import Driver


@sysactions.action
def get_kiosk_configurations(pos_id):
    config = cfgtools.read(os.environ["LOADERCFG"])
    screen_timeout = config.find_value("KioskConfig.ScreenTimeout")
    cancel_timeout = config.find_value("KioskConfig.CancelTimeoutWindow")
    top_banner_timeout = config.find_value("KioskConfig.TopBannerTimeout")
    kiosk_context = config.find_value("KioskConfig.KioskContext")
    show_sale_type = (config.find_value("KioskConfig.ShowSaleType") or "false").lower() == "true"
    supported_langs = config.find_values("KioskConfig.SupportedLangs")

    # TODO: get kiosk configuration correctly
    params = {
        'descr_id': 1
    }
    conn = None
    try:
        conn = Driver().open(mb_context, pos_id, service_name="Persistence")
        cursor = conn.pselect("getDescriptions", **params)
        descriptions = {row.get_entry(0): row.get_entry(1) for row in cursor}
    finally:
        if conn:
            conn.close()

    config = {
        'supportedLangs': supported_langs,
        'screenTimeout': int(screen_timeout),
        'cancelTimeoutWindow': int(cancel_timeout),
        'topBannerTimeout': int(top_banner_timeout),
        'showSaleType': show_sale_type,
        'baseContext': kiosk_context,
        'descriptions': descriptions
    }
    return json.dumps(config)
