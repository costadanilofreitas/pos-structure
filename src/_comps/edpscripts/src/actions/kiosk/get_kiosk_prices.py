# -*- coding: utf-8 -*-

import json

import sysactions
from actions import mb_context
from persistence import Driver


@sysactions.action
def get_kiosk_prices(pos_id):
    conn = None
    params = {
        'pricelist': 'EI'
    }
    try:
        conn = Driver().open(mb_context, pos_id, service_name="Persistence")
        cursor = conn.pselect("getProductPrices", **params)
        products = {row.get_entry(0): {
            'default': float(row.get_entry(1) or 0),
            'added': float(row.get_entry(2) or 0)
        } for row in cursor}

        combos = {}
        cursor = conn.pselect("getCompositions")
        for row in cursor:
            combo_code = row.get_entry(0)
            part_code = row.get_entry(1)
            default_qty = int(row.get_entry(2))
            min_qty = int(row.get_entry(3) or 0)
            part_is_option = int(row.get_entry(4)) == 1
            item_code = row.get_entry(5)
            if part_is_option:
                current_value = _get_best_price(products, "1", combo_code, part_code, item_code.split(','))
            else:
                current_value = _get_best_price(products, "1", combo_code, part_code, [part_code])

            value = current_value * (default_qty or min_qty or 1)

            if not combos.get(combo_code):
                combos[combo_code] = {'default': 0}
            combos[combo_code]['default'] += value

        products.update(combos)
        return json.dumps(products)
    finally:
        if conn:
            conn.close()


def _get_best_price(products, cont, combo_code, part_code, items_list):
    best_price = 99999
    for item_to_find in items_list:
        current_item_price = (
                    products.get('{}.{}.{}.{}'.format(cont, combo_code, part_code, item_to_find)) or
                    products.get('{}.{}.{}'.format(combo_code, part_code, item_to_find)) or
                    products.get('{}.{}'.format(combo_code, item_to_find)) or
                    products.get('{}.{}'.format(part_code, item_to_find)) or
                    products.get('{}.{}'.format(cont, item_to_find)) or
                    products.get(item_to_find) or {}).get('default', 0)
        if 0 < current_item_price < best_price:
            best_price = current_item_price
    if best_price != 99999:
        return best_price
    return 0
