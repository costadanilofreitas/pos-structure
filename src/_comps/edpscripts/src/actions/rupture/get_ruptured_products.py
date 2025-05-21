# -*- coding: utf-8 -*-
import json

import sysactions
from bustoken import TK_REMOTE_ORDER_GET_RUPTURED_ITEMS
from msgbus import TK_SYS_NAK, FM_PARAM
from typing import List

from .. import logger
from .. import mb_context


@sysactions.action
def get_ruptured_products(pos_id, disabled_json, updated_disabled_json):
    # type: (str, str, str) -> str
    
    try:
        disabled_products = _get_ruptured_products_from_json(disabled_json)
        updated_disabled_products = _get_ruptured_products_from_json(updated_disabled_json)

        new_disabled_products = [x for x in updated_disabled_products if x not in disabled_products]
        new_enabled_products = [x for x in disabled_products if x not in updated_disabled_products]

        products = {
                "enabledProducts": new_enabled_products,
                "disabledProducts": new_disabled_products
        }
        
        return json.dumps(products)

    except Exception as e:
        logger.exception('[get_ruptured_products] Exception {}'.format(e))
        sysactions.show_messagebox(pos_id, "$RUPTURE_ERROR", "$INFORMATION")


def _get_ruptured_products_from_json(products_json):
    # type: (str) -> List
    
    products = json.loads(products_json)
    products_list = []
    for product in products:
        products_list.append(product["product_code"])
        
    ruptured_products = _get_ruptured_products(products_list)
    return ruptured_products


def _get_ruptured_products(products):
    # type: (List) -> List
    
    msg = mb_context.MB_EasySendMessage("RemoteOrder", TK_REMOTE_ORDER_GET_RUPTURED_ITEMS, FM_PARAM,
                                        json.dumps(products))
    if msg.token == TK_SYS_NAK:
        raise Exception(msg.data)
    
    return json.loads(msg.data)
