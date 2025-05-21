import json
import persistence
import time

from datetime import datetime, timedelta
from threading import Lock

from sysactions import get_podtype, action, get_model
from systools import sys_log_exception

from .. import mb_context
from ..util import get_ruptured_products

_product_price = {}
product_by_barcode = {}
rupture_treated_events = []
products_cache = None
last_cache_time = None
lock = Lock()


@action
def getProducts(pos_id, seconds_to_renew_cache=180):
    global products_cache
    global rupture_treated_events
    global last_cache_time

    with lock:
        now = datetime.now()
        seconds_to_renew = _get_seconds_to_renew(seconds_to_renew_cache)
        if not products_cache or _reached_seconds_to_renew_cache(now, seconds_to_renew):
            last_cache_time = now
            products_cache = _get_products(pos_id)

    return json.dumps(products_cache)


def _get_seconds_to_renew(seconds_to_renew_cache):
    seconds_to_renew = 180
    try:
        seconds_to_renew = int(seconds_to_renew_cache)
    except TypeError as _:
        pass
    return seconds_to_renew


def _rupture_is_already_handled(rupture_event_id):
    return rupture_event_id is None or rupture_event_id in rupture_treated_events


def _reached_seconds_to_renew_cache(now, seconds_to_renew_cache):
    return not last_cache_time or now > last_cache_time + timedelta(seconds_to_renew_cache)


def _get_products(pos_id):
    global product_by_barcode
    product_by_barcode = {}

    query = """SELECT P.ProductCode,
                P.ProductName,
                PCP.CustomParamValue AS BarCode,
                NULLIF(Production.JITLines,'None') AS ProductionLine,
                CASE WHEN COALESCE(PT.Tag, PCP1.CustomParamValue) IS NULL THEN 'false' ELSE 'true' END AS CFH
                FROM Product P
                LEFT JOIN Production ON Production.ProductCode=P.ProductCode
                LEFT JOIN ProductCustomParams PCP ON PCP.ProductCode=P.ProductCode AND PCP.CustomParamId='BarCode'
                LEFT JOIN ProductCustomParams PCP1 ON PCP1.ProductCode=P.ProductCode AND PCP1.CustomParamId='CFH'
                AND PCP1.CustomParamValue = 'true'
                LEFT JOIN ProductTags PT ON PT.ProductCode=P.ProductCode AND PT.Tag='CFH=true'
                ORDER BY P.ProductName"""
    prices = get_prices(pos_id)
    prod_list = {}

    try:
        ruptured_items = get_ruptured_products()
        conn = persistence.Driver().open(mb_context, dbname=str(pos_id))
        cursor = conn.select(query)
        for row in cursor:
            plu, name, barcode, prodline, cfh = map(row.get_entry, ("ProductCode", "ProductName", "BarCode", "ProductionLine", "CFH"))
            product = {
                "plu": plu,
                "name": name,
                "price": prices.get(plu),
                "barcode": barcode,
                "prodline": prodline,
                "ruptured": plu in ruptured_items,
                "CFH": cfh
            }
            prod_list[plu] = product
            if barcode:
                product_by_barcode[int(barcode)] = product
    except:
        sys_log_exception("Error getting product list")
    return prod_list


@action
def getPrices(pos_id):
    return json.dumps(get_prices(pos_id))


def get_prices(pos_id):
    part_data = {}
    tag_data = {}
    price_data = {}
    conn = persistence.Driver().open(mb_context, dbname=str(pos_id))
    part_data = _get_part_data(conn)
    tag_data = _get_tag_data(conn)
    price_data = _get_price_data(conn, get_podtype(get_model(pos_id)) == "DL")

    prices = price_data

    def try_to_get_price(part_code, part_context):
        return price_data.get(part_code, {}).get(part_context) or price_data.get(part_code, {}).get(None) or 0

    def get_price_by_product_type_recursively(part_entries, product):
        price = try_to_get_price(product, '1')
        for part_params in part_entries:
            product_type = part_params["product_type"]
            part_code = part_params["part_code"]

            full_context = "{}.{}".format(product, part_code)
            if product_type == 0:  # product
                price += try_to_get_price(part_code, product)
            elif product_type == 1:  # option
                default_part = tag_data.get(product.split('.')[-1], {}).get(part_code)
                if default_part:
                    price += try_to_get_price(default_part, full_context)
                else:
                    price += try_to_get_price(part_params["product_codes"][0], full_context)
            elif product_type == 2 and part_code in part_data:
                price += get_price_by_product_type_recursively(part_data[part_code], "{}.{}".format(full_context, part_code))
        return price

    for product, part_entries in part_data.iteritems():
        prices[product] = {None: get_price_by_product_type_recursively(part_entries, product)}

    return prices


def get_product_by_barcode(barcode):
    if barcode and int(barcode) in product_by_barcode:
        return product_by_barcode[int(barcode)]

    return None


def get_product_price_from_cache(plu, pos_id):
    if _product_price == {}:
        _get_products(pos_id)
    return _product_price[int(plu)]


def _get_part_data(conn):
    part_data = {}
    cursor = conn.select("""
        SELECT
            part.productCode,
            part.partcode,
            part.defaultQty,
            params.ProductType,
            class.ProductCodes
        FROM ProductPart part
        JOIN ProductKernelParams params
            ON params.ProductCode = part.PartCode
        LEFT JOIN (
            SELECT
                classcode,
                group_concat(ProductCode) as ProductCodes
            FROM ProductClassification
            GROUP BY ClassCode
        ) class
             ON class.ClassCode = part.PartCode
        WHERE part.MinQty > 0
        ORDER BY part.ProductCode;
        """)
    for row in cursor:
        part_data.setdefault(row.get_entry(0), []).append({
            "part_code": row.get_entry(1),
            "default_qty": row.get_entry(2),
            "product_type": int(row.get_entry(3)),
            "product_codes": (row.get_entry(4) or "").split(',')
        })
    return part_data


def _get_tag_data(conn):
    tag_data = {}
    cursor = conn.select("""
        SELECT substr(Tag, 12), ProductCode
        FROM ProductTags
        WHERE Tag LIKE 'HasOptions=%'
        """)
    for row in cursor:
        entry_data = {}
        for option_data in row.get_entry(0).split('|'):
            option_code, default_option = option_data.split('>')
            if not default_option:
                continue
            entry_data[option_code] = default_option
        tag_data[row.get_entry(1)] = entry_data
    return tag_data


def _get_price_data(conn, is_delivery):
    price_data = {}
    cursor = conn.select("""
        SELECT ProductCode, Context, COALESCE(CAST(DefaultUnitPrice AS FLOAT), 0)
        FROM Price
        WHERE PriceListId = '{}' AND DATETIME('now') BETWEEN ValidFrom AND ValidThru;
        """.format("DL" if is_delivery else "EI"))
    for row in cursor:
        product_code, context, price = row
        if product_code not in price_data:
            price_data[product_code] = {context: float(price)}
        else:
            price_data[product_code][context] = float(price)
    return price_data
