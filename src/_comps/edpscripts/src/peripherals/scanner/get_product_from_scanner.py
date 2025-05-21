import logging

from actions.products.get_products import getProducts, get_product_by_barcode, get_product_price_from_cache
from sysactions import get_model, get_podtype, show_messagebox
from systools import sys_log_exception

logger = logging.getLogger("PosActions")


def sell_product_by_barcode(pos_id, barcode_number, check_consistency=False, received_qty="1"):
    try:

        from posactions import doSale, doCompleteOption, doChangeQuantity
        if not barcode_number:
            return "False"

        logger.info("Barcode {0} ".format(barcode_number))
        if check_consistency and not _is_a_valid_ean13(barcode_number):
            ret = show_messagebox(pos_id, "$BARCODE_WRONG", buttons="$OK|$CANCEL")
            if ret == 0:
                return "Clear"
            return "False"
        model = get_model(pos_id)
        pod_type = get_podtype(model)
        if str(barcode_number).zfill(13).startswith('2'):
            plu, calc_qty = _ticket_from_scale(str(barcode_number), pos_id)
            if pod_type == 'TT':
                doChangeQuantity(int(pos_id), None, str(calc_qty))
                doSale(str(pos_id), '1.' + str(plu), str(calc_qty))
            else:
                doChangeQuantity(int(pos_id), None, str(calc_qty))
                doCompleteOption(str(pos_id), "1", plu, calc_qty)
        else:
            product_by_barcode = get_product_by_barcode(barcode_number)
            if product_by_barcode:
                if product_by_barcode["ruptured"]:
                    logger.info("Scanned barcode {0} product is ruptured!".format(barcode_number))
                    ret = show_messagebox(pos_id,
                                          "$BARCODE_PRODUCT_RUPTURED|{}".format(product_by_barcode["name"]),
                                          buttons="$YES|$NO")
                    if ret != 0:
                        return "Clear"

                if pod_type == 'TT':
                    doSale(str(pos_id), '1.' + str(product_by_barcode['plu']), received_qty)
                else:
                    doCompleteOption(str(pos_id), "1", product_by_barcode['plu'], received_qty)
            else:
                logger.info("Scanned barcode {0} not found on the product database!".format(barcode_number))
                ret = show_messagebox(pos_id, "$BARCODE_NOT_FOUND|{}".format(barcode_number), buttons="$OK|$CANCEL")
                if ret == 0:
                    return "Clear"
                return "False"
        return "True"
    except Exception as _:
        sys_log_exception("Error on [sell_product_by_barcode]")
        logger.exception("Error on [sell_product_by_barcode]")
        return "False"


def _is_a_valid_ean13(barcode):
    if len(str(barcode)) != 13:
        return False
    barcode = list(str(barcode).zfill(13))
    index = 0
    value = 0
    dv = barcode.pop()
    for x in barcode:
        value = value + (int(x) * ((index % 2) * 2 + 1))
        index += 1
    value2 = (((int(value / 10) + 1) * 10) - value) % 10
    if value2 != int(dv):
        return False
    return True


def _ticket_from_scale(barcode, pos_id):
    from posactions import scale_ticket_mode
    plu = int(barcode[1:7])
    param = int(barcode[7:12])
    if scale_ticket_mode == 'price':
        final_price = float(param) / 100
        price = float(get_product_price_from_cache(plu, pos_id))
        qtd = round((final_price / price), 3)
    else:
        qtd = round(float(param) / 1000, 3)
    return str(plu), qtd
