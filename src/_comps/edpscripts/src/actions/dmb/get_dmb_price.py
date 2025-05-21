import json

import persistence
from sysactions import action, get_model, format_amount

from .. import mb_context, logger

_products_cache = None

@action
def get_dmb_prices(pos_id):
    products = _get_products()

    price_list = [{"position": 0, "itemId": "100001", "price": 0},
                  {"position": 1, "itemId": "100002", "price": 0},
                  {"position": 2, "itemId": "100005", "price": 0},
                  {"position": 3, "itemId": "100003", "price": 0},
                  {"position": 4, "itemId": "100600", "price": 0},
                  {"position": 5, "itemId": "100025", "price": 0},
                  {"position": 6, "itemId": "220001.220003.220010", "price": 0},
                  {"position": 7, "itemId": "100018", "price": 0},
                  {"position": 8, "itemId": "100019", "price": 0},
                  {"position": 9, "itemId": "100108", "price": 0},
                  {"position": 10, "itemId": "100083", "price": 0}]

    for product in price_list:
        if product["itemId"] in products:
            product["price"] = products[product["itemId"]]

    return json.dumps(price_list)


def _get_products(pos_id="1"):
    global _products_cache

    model = get_model(pos_id)

    if _products_cache is None:
        query = """select ProductCode, Context, DefaultUnitPrice from price"""
        products = {}
        conn = None
        try:
            conn = persistence.Driver().open(mb_context)
            cursor = conn.select(query)
            for row in cursor:
                part_code, context, price = map(row.get_entry, ("ProductCode", "Context", "DefaultUnitPrice"))
                item_id = str(part_code)
                if context is not None:
                    item_id = context + "." + item_id

                products[item_id] = format_amount(model, price)
        except:
            logger.exception("Error getting product list")
        finally:
            if conn:
                conn.close()
        _products_cache = products

    return _products_cache
