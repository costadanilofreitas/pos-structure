# -*- encoding: utf-8 -*-

import decimal
import json
import logging
import time
from copy import deepcopy
from datetime import datetime
from decimal import Decimal as D
from xml.etree import cElementTree as etree

import persistence
import posactions
import pyscripts
from actions.eft import finish_eft_transactions
from custom_sysactions import user_authorized_to_execute_action
from mw_helper import show_filtered_list_box_dialog, show_numpad_dialog
from posot import OrderTakerException
from sysactions import get_model, get_posot, show_info_message, show_messagebox, get_current_order, get_pricelist, \
    StopAction, get_operator_session
from systools import sys_log_info, sys_log_exception, sys_log_error, sys_log_warning

# Promotion script types
MANUAL = 0          # : Script must be manually executed (thru a button, for example)
ON_TOTAL = 1        # : Script is automatically called when a sale is totalized
ON_ITEMSALE = 2     # : Script is automatically called when an item is sold

mbcontext = pyscripts.mbcontext
_promotions = {}

logger = logging.getLogger("PosActions")


def main():
    if not hasattr(posactions.on_before_total, 'callbacks'):
        posactions.on_before_total.callbacks = []
    posactions.on_before_total.callbacks.append(check_order_coupons)
    posactions.on_before_total.callbacks.append(on_before_total)


def on_before_total(posid, model=None, *args):
    """
    Function used to connect to posactions.on_before_total and act like as an event-listener.
    @param posid: POS id
    @param model: POS model
    """
    to_run = [script for (
        script, promo) in _promotions.iteritems() if promo._promotype == ON_TOTAL]
    if to_run:
        model = model or get_model(posid)
        try:
            posot = get_posot(model)
            discounts = etree.XML(posot.getOrderDiscounts(applied=False))
            for script in to_run:
                for discount in discounts.findall("OrderDiscount"):
                    if discount.get("discountScript") == script:
                        discountid = str(discount.get("discountId"))
                        sys_log_info(
                            "Running automatic promotion script [%s] on POS [%s]" % (script, posid))
                        _promotions[script](
                            posid, discountid, {"model": model})
        except OrderTakerException, e:
            logger.error('ERROR {}'.format(e))
            show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
                e.getErrorCode(), e.getErrorDescr()), msgtype="critical")
    return True


def check_order_coupons(posid, model=None, coupon_list=[], only_check=False, available_coupons=None, *args):
    """
    Function used to connect to posactions.on_before_total and act like as an event-listener for coupons.
    @param posid: POS id
    @param model: POS model
    @param coupon_list: (optional) List of tuples of (line number, part code) to be used for validations. Provided thru the action 'doCouponDiscount'.
    """
    coupons = available_coupons or get_available_coupons(posid)
    model = model or get_model(posid)
    posot = get_posot(model)
    order = get_current_order(model)
    order_total = D(order.get("totalGross"))
    if not coupon_list:
        coupon_list = [(line.get("lineNumber"), line.get("partCode")) for line in order.findall("SaleLine") if float(line.get("qty")) > 0 and int(line.get("level")) == 0]
    if not coupon_list:
        return True

    sale_lines = []
    for line in order.findall("SaleLine"):
        if int(line.get("level")) != 0:
            continue
        if D(line.get("itemDiscount") or "0.00") > D("0.00"):
            continue
        sale_lines.append(dict(line.attrib.items()))
    sale_lines = sorted(sale_lines, key=lambda sl: D(line.get("unitPrice", "0")))

    for line_number, product_code in coupon_list:
        coupon = get_coupon_by_product_code(posid, product_code, coupons)
        coupon_original = get_coupon_by_product_code(posid, product_code, coupons)
        if coupon is None:
            coupon_code = ''
            if only_check:
                show_messagebox(posid, "Invalid coupon code [{0}].".format(coupon_code), icon="warning")
                return False
            continue

        coupon_code = coupon["code"]
        coupon["reqType"] = coupon["reqType"].upper()
        coupon["type"] = coupon["type"].upper()
        times_satisfied = None
        try:
            if "reqMinimalOrderTotal" in coupon and order_total < D(coupon["reqMinimalOrderTotal"]):
                show_messagebox(posid, "Minimal order total for coupon code [{0}] is [{1}].".format(coupon_code, coupon["reqMinimalOrderTotal"]), icon="warning")
                raise Exception("Minimal order total for coupon code [{0}] is [{1}].".format(coupon_code, coupon["reqMinimalOrderTotal"]))
            if any(k in coupon for k in("reqTag", "reqProd")):
                if coupon["reqType"] in ("TAG-ALL", "TAG-ANY"):
                    tag_idx = -1
                    while True:
                        tag_idx += 1
                        if tag_idx >= len(coupon["reqTag"]):
                            break
                        reqqty = coupon["reqQty"][tag_idx] or 1
                        reqprod = get_products_by_tag(posid, coupon["reqTag"][tag_idx])
                        for reqcode in reqprod.keys():
                            for line in sale_lines:
                                qty = float(line.get("qty"))
                                pcode = int(line.get("partCode"))
                                if pcode == int(reqcode):
                                    reqqty -= qty
                        coupon["reqQty"][tag_idx] = reqqty
                else:
                    for idx, reqcode in enumerate(coupon["reqProd"]):
                        reqqty = coupon["reqQty"][idx] or 1
                        if reqqty > 0:
                            for line in sale_lines:
                                qty = float(line.get("qty"))
                                pcode = int(line.get("partCode"))
                                if pcode == reqcode:
                                    reqqty -= qty
                        coupon["reqQty"][idx] = reqqty
                if coupon["reqType"].endswith("ALL"):
                    if not all(q <= 0 for q in coupon["reqQty"]):
                        show_messagebox(posid, "$COUPON_PREREQ_FAILED|{}".format(coupon_code), icon="warning")
                        raise Exception("Not all pre-requirements for coupon code [{0}] were satisfied.".format(coupon_code))
                    idx = 0
                    for q in coupon["reqQty"]:
                        num = int(((q - 1) * (-1))/coupon_original["reqQty"][idx])
                        idx += 1
                        if (times_satisfied is None) or times_satisfied > num:
                            times_satisfied = num

                elif coupon["reqType"].endswith("ANY"):
                    if not any(q <= 0 for q in coupon["reqQty"]):
                        show_messagebox(posid, "$COUPON_PREREQ_FAILED|{}".format(coupon_code), icon="warning")
                        raise Exception("Not all pre-requirements for coupon code [{0}] were satisfied.".format(coupon_code))
                    idx = 0
                    times_satisfied = 0
                    for q in coupon["reqQty"]:
                        if q <= 0:
                            times_satisfied += int(((q - 1) * (-1))/coupon_original["reqQty"][idx])
                        idx += 1
            if only_check:
                continue

            if coupon["type"] in ("ITEM", "ITEM-PROMO"):
                try:
                    max_discount_products = None
                    multiple_discount_products = 1

                    if coupon["type"] == "ITEM-PROMO":
                        multiple_discount_products = coupon["discQty"]
                    if "discQty" in coupon:
                        if times_satisfied:
                            max_discount_products = int(coupon["discQty"]) * times_satisfied
                    else:
                        max_discount_products = None

                    if "discTag" in coupon:
                        discprod = get_products_by_tag(posid, coupon["discTag"])
                        coupon["discProd"] = discprod.keys()

                    promo_price_split = None
                    promo_price_split_residue = D(0)
                    to_be_discounted_product = []
                    qty_total_found = 0
                    overhead_qty = 0

                    promo_price = D(coupon["promoPrice"]) if "promoPrice" in coupon else None

                    if promo_price is not None:
                        promo_price_split = promo_price / D(coupon["discQty"])
                        promo_price_split = promo_price_split.quantize(D('.01'), decimal.ROUND_HALF_DOWN)
                        if promo_price_split * D(coupon["discQty"]) != promo_price:
                            promo_price_split_residue = promo_price - (promo_price_split * D(coupon["discQty"]))

                    for line in sale_lines:
                        if int(line.get("partCode")) in coupon["discProd"] and float(line.get("qty")) > 0:
                            if (max_discount_products and qty_total_found < max_discount_products) or max_discount_products is None:
                                if promo_price is not None:
                                    discount_amount = D(line.get("qty")) * (D(line.get("unitPrice", "0")) - promo_price_split) + D(promo_price_split_residue)
                                    promo_price_split_residue = D(0)
                                else:
                                    discount_amount = (D(line.get("qty")) * D(coupon["discAmt"])) if "discAmt" in coupon else (
                                                D(line.get("qty")) * D(coupon["discRate"]) / D(100) * D(line.get("unitPrice", "0")))

                                to_be_discounted_product.append({
                                    "partCode": line.get("partCode"),
                                    "qty": float(line.get("qty")),
                                    "discountid": str(coupon["discountId"]),
                                    "discountamt": discount_amount,
                                    "linenumber": line.get("lineNumber"),
                                    "itemid": line.get("itemId"),
                                    "level": line.get("level"),
                                    "partcode": line.get("partCode"),
                                    "unitprice": D(line.get("unitPrice", "0")),
                                    "forcebyitem": 0
                                })
                                qty_total_found += float(line.get("qty"))

                    if max_discount_products and qty_total_found > max_discount_products:
                        overhead_qty = qty_total_found - max_discount_products
                    if (qty_total_found-overhead_qty) % multiple_discount_products > 0:
                        overhead_qty += (qty_total_found-overhead_qty) % multiple_discount_products

                    if overhead_qty > 0:
                        for product_line in to_be_discounted_product:
                            if overhead_qty == 0:
                                break
                            if product_line['qty'] <= overhead_qty:
                                overhead_qty -= product_line['qty']
                                product_line['discountamt'] = 0
                            elif product_line['qty'] > overhead_qty:
                                posot.splitOrderLine(posid, product_line['linenumber'], (product_line['qty'] - overhead_qty))
                                product_line['qty'] = (product_line['qty'] - overhead_qty)
                                overhead_qty = 0
                                if promo_price is not None:
                                    product_line['discountamt'] = (D(product_line['qty']) * (
                                            product_line['unitprice'] - promo_price_split)) + D(
                                        promo_price_split_residue)
                                    promo_price_split_residue = D(0)
                                else:
                                    product_line['discountamt'] = D(product_line['qty']) * D(
                                        coupon["discAmt"]) if "discAmt" in coupon else (
                                                D(product_line['qty']) * (D(coupon["discRate"]) / D(100)) * product_line['unitprice'])
                    posot.blkopnotify = True
                    for product_line in to_be_discounted_product:
                        if product_line['discountamt'] > 0:
                            posot.clearDiscount(discountid=coupon['discountId'], linenumber=product_line['linenumber'],
                                                itemid=product_line['itemid'], level=product_line['level'],
                                                partcode=product_line['partcode'])
                            posot.applyDiscount(product_line["discountid"], product_line["discountamt"], product_line["linenumber"], product_line["itemid"],
                                                product_line["level"], product_line["partcode"], product_line["forcebyitem"])
                            logger.debug(
                                'Aplicando desconto de %s na linha %s' % (product_line["discountamt"], product_line["linenumber"]))
                    posot.blkopnotify = False
                    posot.updateOrderProperties(posid)

                except OrderTakerException, e:
                    logger.error('ERROR {}'.format(e))
                    show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (e.getErrorCode(), e.getErrorDescr()), msgtype="critical")
                    raise
            elif coupon["type"].upper() == "ORDER":
                try:
                    posot = get_posot(model)
                    discountamt = D(coupon["discAmt"] if "discAmt" in coupon else ((D(coupon["discRate"]) / D(100)) * order_total))

                    posot.blkopnotify = True
                    posot.clearDiscount(coupon["discountId"])
                    posot.applyDiscount(coupon["discountId"], discountamt, forcebyitem=1)
                    posot.blkopnotify = False
                    posot.updateOrderProperties(posid)

                    logger.debug('Aplicando desconto de %s na venda inteira' % discountamt)
                except OrderTakerException, e:
                    logger.error('ERROR {}'.format(e))
                    show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (e.getErrorCode(), e.getErrorDescr()), msgtype="critical")
                    raise
        except Exception, e:
            logger.error('ERROR {}'.format(e))
            logger.error('ERRO NA APLICAÇÃO DE DESCONTO: %s' % e)
            if not only_check:
                try:
                    posot.voidLine(posid, line_number)
                except Exception, e:
                    logger.error('ERROR {}'.format(e))
                    sys_log_warning("Failed to remove coupon [{0}] product code [{1}] at line [{2}] after a couponp processing error !!!".format(coupon_code, product_code, line_number))
                sys_log_exception("Exception occurred when processing coupon code[{0}] product code [{1}] at line [{2}] after a coupon processing error !!!".format(coupon_code, product_code, line_number))
            else:
                return False

    return True


def get_product_price(posid, itemid):
    conn = None
    price = None
    try:
        sql = """
            SELECT (SELECT DefaultUnitPrice FROM productdb.Price WHERE PriceKey=PP.PriceKey) AS UnitPrice,
                   CASE PP.PriceListId
                      WHEN O.PriceListId1 THEN 1
                      WHEN O.PriceListId2 THEN 2
                      WHEN O.PriceListId3 THEN 3
                   END AS PriceOrder
            FROM orderdb.Orders O
            JOIN sysproddb.ProductPrice PP
              ON PP.PriceListId IN (O.PriceListId1, O.PriceListId2, O.PriceListId3)
            WHERE PP.ItemId='%s' AND
                  DATE(o.createdAt) BETWEEN PP.ValidFrom AND PP.ValidThru AND
                  O.OrderId=(SELECT CurrentOrder FROM orderdb.POS)
            ORDER BY PriceOrder DESC
            LIMIT 1
        """ % (itemid)
        conn = persistence.Driver().open(mbcontext, dbname=str(posid))
        cursor = conn.select(sql)
        for row in cursor:
            price = row.get_entry(0)
            break
    except Exception, e:
        logger.error('ERROR {}'.format(e))
        sys_log_exception("Unable to acquire product current price")
    finally:
        if conn:
            conn.close()
    return price


@posactions.action
@user_authorized_to_execute_action
def doApplicableCoupons(pos_id, auth_data, *args, **kwargs):
    return apply_discount(pos_id, auth_data)


def apply_discount(pos_id, auth_data):
    success = False

    model = get_model(pos_id)
    pos_ot = get_posot(model)
    price_list = get_pricelist(model)
    order = get_current_order(model)
    session_id = get_operator_session(model)
    operator = session_id.split("user=")[-1].split(",")[0]
    authorizer = auth_data[0] if auth_data else None

    try:
        coupon_codes, coupons, coupons_available = _get_available_discounts(pos_id)
        selected_index = _select_discount(pos_id, coupons)
        if selected_index is None:
            success = False
            return

        coupon = filter(lambda c: c["index"] == selected_index + 1, coupons)
        if not coupon:
            success = False
            return

        coupon = coupon[0]
        logger.debug("Selected discount coupon description: {}".format(coupon['descr']))

        if coupon['index'] in [1, 2]:
            if not clean_discounts_and_payments(pos_id, pos_ot, order):
                success = False
                return

            time.sleep(0.5)  # kernel update delay
            model = get_model(pos_id)
            order = get_current_order(model)
            apply_amount_discount(pos_id, pos_ot, order, coupon=coupon)
            success = True
            return

        if check_order_coupons(pos_id, model=model, coupon_list=[("-1", coupon["code"])], available_coupons=coupons_available, only_check=True):
            sale_line = pos_ot.doSale(int(pos_id), itemid="1.{0}".format(coupon["code"]), pricelist=price_list, qtty=1, verifyOption=False, aftertotal="1")
            sale_line = etree.XML(sale_line)
            order_lines = [(line.get("lineNumber"), line.get("partCode")) for line in order.findall("SaleLine") if float(line.get("qty")) > 0 and int(line.get("level")) == 0 and line.get("partCode") not in coupon_codes]
            order_lines.append((sale_line.get("lineNumber"), sale_line.get("partCode")))
            success = check_order_coupons(pos_id, model=model, coupon_list=order_lines, available_coupons=coupons_available)
            return

    except Exception as _:
        error_msg = "Error applying discount"
        sys_log_exception(error_msg)
        logger.exception(error_msg)
        success = False

    finally:
        if success:
            pos_ot.setOrderCustomProperties({"DISCOUNT_APPLY_DATETIME": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                                             "DISCOUNT_APPLY_OPERATOR": operator,
                                             "DISCOUNT_APPLY_AUTHORIZER": authorizer if authorizer is not None else operator,
                                             "DISCOUNT_APPLY_METHOD": coupon['descr']})

        return success


@posactions.action
@user_authorized_to_execute_action
def clean_discounts(pos_id):
    lines_to_void = {}
    model = get_model(pos_id)
    pos_ot = get_posot(model)
    order = model.find(".//Order")
    sale_lines = order.findall(".//SaleLine")
    for sale_line in sale_lines:
        item_type = sale_line.get("itemType")
        qty = int(sale_line.get('qty'))
        if item_type == "COUPON" and qty > 0:
            line_number = sale_line.get("lineNumber")
            order_id = order.get("orderId")
            if order_id in lines_to_void:
                lines_to_void[order_id].append(line_number)
            lines_to_void[order_id] = [line_number]

    if len(lines_to_void) > 0:
        for order_id in lines_to_void:
            pos_ot.voidLine(int(pos_id), "|".join(lines_to_void[order_id]))
            pos_ot.clearDiscount()
    else:
        pos_ot.clearDiscount()


def get_available_coupons(posid):
    conn = None
    coupons = []
    try:
        sql = """
            SELECT
                A.ProductCode AS CouponInternalCode,
                A.ProductName AS CouponDescription,
                C.CustomParamValue AS CouponAttributes,
                D.ValidFrom AS ValidFrom,
                D.ValidThru AS ValidThru,
                B.ProductPriority AS Priority
            FROM Product A
            JOIN ProductKernelParams B ON B.ProductCode=A.ProductCode AND B.ProductType=(SELECT TypeId FROM productdb.ProductType WHERE TypeDescr='TYPE_COUPON' LIMIT 1)
            JOIN ProductCustomParams C ON C.ProductCode=B.ProductCode AND CustomParamId='COUPON_ATTRIBUTES'
            LEFT JOIN discountcalc.Discounts D On D.DiscountId=JSONGet('discountId', C.CustomParamValue)
            WHERE B.Enabled=1
        """
        conn = persistence.Driver().open(mbcontext, dbname=str(posid))
        cursor = conn.select(sql)
        coupons = [dict(zip(map(cursor.get_name, (0, 1, 2, 3, 4, 5)), map(row.get_entry, (0, 1, 2, 3, 4, 5)))) for row in cursor]
        for c in coupons:
            c["CouponAttributes"] = json.loads(c["CouponAttributes"])
            c["CouponAttributes"]["productCode"] = c["CouponInternalCode"]
            c["CouponAttributes"]["couponDescription"] = c["CouponDescription"]
            c["CouponAttributes"]["validFrom"] = c["ValidFrom"]
            c["CouponAttributes"]["validThru"] = c["ValidThru"]
            c["CouponAttributes"]["priority"] = c["Priority"]
        coupons = sorted([c["CouponAttributes"] for c in coupons], key=lambda i: i["priority"])
    except Exception, e:
        logger.error('ERROR {}'.format(e))
        sys_log_exception("Unable to parse and build coupons dictionary")
    finally:
        if conn is not None:
            conn.close()
    return coupons


def get_products_by_tag(posid, tag):
    conn = None
    products = {}
    try:
        sql = """
            SELECT
                A.ProductCode AS ProductCode,
                A.ProductName AS ProductName
            FROM Product A
            JOIN ProductKernelParams B ON B.ProductCode=A.ProductCode AND B.Enabled=1
            JOIN ProductTags C ON C.ProductCode=B.ProductCode AND Tag='{0}'
        """.format(tag)
        conn = persistence.Driver().open(mbcontext, dbname=str(posid))
        cursor = conn.select(sql)
        products = dict([(row.get_entry(0), row.get_entry(1)) for row in cursor])
    except Exception, e:
        logger.error('ERROR {}'.format(e))
        sys_log_exception("Unable to acquire product current price")
    finally:
        if conn is not None:
            conn.close()
    return products


def get_coupon_by_code(posid, coupon_code, coupons=[]):
    if not coupons:
        coupons = get_available_coupons(posid)
    if coupons:
        coupon = filter(lambda c: True if c.get("code", "") == str(coupon_code) else False, coupons)
        if not coupon:
            return None
        coupon = deepcopy(coupon[0])
        if not all(k in coupon for k in("type", "discountId", "code", "reqType")) or \
            not any(k in coupon for k in("discAmt", "discRate", "promoPrice")) or \
            coupon["type"].upper() not in ("ITEM", "ORDER", "ITEM-PROMO") or \
            coupon["reqType"].upper() not in ("ALL", "ANY", "TAG"):
            sys_log_error("Invalid setup of coupon code [{0}]: invalid coupon description".format(coupon["code"]))
            return None
        return coupon
    return None


def get_coupon_by_product_code(posid, product_code, coupons=[]):
    logger.debug(coupons)
    logger.debug(product_code)
    if not coupons:
        coupons = get_available_coupons(posid)
    if coupons:
        coupon = filter(lambda c: True if c.get("productCode", "") == str(product_code) else False, coupons)
        logger.debug(coupon)
        if not coupon:
            return None
        coupon = deepcopy(coupon[0])
        if  not all(k in coupon for k in("type", "discountId", "code", "reqType")) or \
            not any(k in coupon for k in("discAmt", "discRate", "promoPrice")) or \
            coupon["type"].upper() not in ("ITEM", "ORDER", "ITEM-PROMO") or \
            coupon["reqType"].upper() not in ("ALL", "ANY", "TAG-ALL", "TAG-ANY"):
            sys_log_error("Invalid setup of coupon code [{0}]: invalid coupon description".format(coupon["code"]))
            return None
        logger.debug('cupom validado - %s' % product_code)
        return coupon
    return None


def clean_discounts_and_payments(pos_id, pos_ot, order):
    from table_actions import clean_order_discounts
    clean_order_discounts(pos_id, pos_ot, order)
    clean_order_discount_properties(pos_ot)
    return _clean_order_payments(pos_id, pos_ot, order)


def clean_order_discount_properties(pos_ot):
    pos_ot.setOrderCustomProperty("DISCOUNT_APPLY_DATETIME")
    pos_ot.setOrderCustomProperty("DISCOUNT_APPLY_OPERATOR")
    pos_ot.setOrderCustomProperty("DISCOUNT_APPLY_AUTHORIZER")
    pos_ot.setOrderCustomProperty("DISCOUNT_APPLY_METHOD")


def _clean_order_payments(pos_id, posot, order):
    order_tenders = order.findall(".//Tender")
    if len(order_tenders) >= 1:
        ret = show_messagebox(pos_id, "$CLEAN_TENDERS_TO_APPLY_DISCOUNT", buttons="$YES|$NO")
        if ret != 0:
            return False
        posot.clearTenders(pos_id)
        finish_eft_transactions(pos_id, order, "1")

    return True


def _get_available_discounts(pos_id):
    coupons_available = get_available_coupons(pos_id)
    coupons = [{"code": 1, "descr": 'Valor', "index": 1}, {"code": 2, "descr": 'Porcentagem', "index": 2}]
    coupons.extend([{"code": t["productCode"], "descr": t["couponDescription"], "index": i + 3} for i, t in
                    enumerate(coupons_available)])
    coupons = sorted(coupons, key=lambda c: c["index"])
    coupon_codes = [c["code"] for c in coupons]
    return coupon_codes, coupons, coupons_available


def _select_discount(pos_id, coupons):
    options = ["{0} - {1}".format(coupon["index"], coupon["descr"]) for coupon in coupons]
    return show_filtered_list_box_dialog(pos_id, options, "Selecione o Cupom:", mask="NOFILTER")


def apply_amount_discount(pos_id, posot, order, coupon=None, discount_type=None, discount_value=None):
    if not discount_type:
        discount_type = coupon['index']
        title = "$DISCOUNT_VALUE_TITLE" if discount_type == 1 else "$DISCOUNT_PERCENTAGE_TITLE"
        mask = "CURRENCY" if discount_type == 1 else "NUMBER"
        if not discount_value:
            discount_value = show_numpad_dialog(pos_id, title, "", mask)
            if discount_value is None:
                return False

    if not clean_discounts_and_payments(pos_id, posot, order):
        return False

    amount = float(order.get("totalGross"))
    if discount_type == 1:
        amount = discount_value if discount_value <= amount else amount

    else:
        amount = (amount * discount_value) / 100

    posot.applyDiscount(1, amount, forcebyitem=1)
