# -*- encoding: utf-8 -*-
# Python module responsible to implement scriptable "promotions and discounts"
#
# Copyright (C) 2008-2010 MWneo Corporation
#
# $Id: pospromotions.py 14270 2014-03-20 19:41:53Z gmamani $
# $Revision: 14270 $
# $Date: 2014-03-20 16:41:53 -0300 (Thu, 20 Mar 2014) $
# $Author: gmamani $

# Python standard modules
import json
import datetime
import time
from xml.etree import cElementTree as etree
from decimal import Decimal as D
# Our modules
import pyscripts
import posactions
import logging
import persistence
from systools import sys_log_info, sys_log_exception, sys_log_error, sys_log_warning
from sysactions import StopAction, get_model, get_posot, show_info_message, show_messagebox, check_current_order, get_authorization, \
    get_current_order, format_amount, show_keyboard, get_business_period, assert_order_discounts, show_listbox, get_pricelist
from posot import OrderTakerException
from copy import deepcopy
import decimal

# Promotion script types
MANUAL = 0          # : Script must be manually executed (thru a button, for example)
ON_TOTAL = 1        # : Script is automatically called when a sale is totalized
ON_ITEMSALE = 2     # : Script is automatically called when an item is sold

# Message-bus context
mbcontext = pyscripts.mbcontext

# Dictionary of promotion scripts
_promotions = {}

logger = logging.getLogger("PosActions")


#
# Main function (called by pyscripts)
#
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
    logger.debug('oioioioioioioioioioioio %s' % only_check)
    coupons = available_coupons or getAvailableCoupons(posid)
    model = model or get_model(posid)
    posot = get_posot(model)
    order = get_current_order(model)
    order_total = D(order.get("totalAmount"))
    logger.debug(coupon_list)
    logger.debug(available_coupons)
    if not coupon_list:
        coupon_list = [(line.get("lineNumber"), line.get("partCode")) for line in order.findall("SaleLine") if int(line.get("qty")) > 0 and int(line.get("level")) == 0]
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
        coupon = getCouponByProductCode(posid, product_code, coupons)
        if coupon is None:
            coupon_code = ''
            if only_check:
                show_messagebox(posid, "Invalid coupon code [{0}].".format(coupon_code), icon="warning")
                return False
            continue
        posot.blkopnotify = True
        coupon_code = coupon["code"]
        coupon["reqType"] = coupon["reqType"].upper()
        coupon["type"] = coupon["type"].upper()
        try:
            if "reqMinimalOrderTotal" in coupon:
                if order_total < D(coupon["reqMinimalOrderTotal"]):
                    show_messagebox(posid, "Minimal order total for coupon code [{0}] is [{1}].".format(coupon_code, coupon["reqMinimalOrderTotal"]), icon="warning")
                    raise Exception("Minimal order total for coupon code [{0}] is [{1}].".format(coupon_code, coupon["reqMinimalOrderTotal"]))

            if coupon["reqType"] in ("TAG-ALL", "TAG-ANY"):
                tag_idx = -1
                while True:
                    tag_idx += 1
                    if tag_idx >= len(coupon["reqTag"]):
                        break
                    reqprod = getProductsByTag(posid, coupon["reqTag"][tag_idx])
                    reqqty = coupon["reqQty"][tag_idx]
                    for reqcode in reqprod.keys():
                        for line in sale_lines:
                            qty = int(line.get("qty"))
                            pcode = int(line.get("partCode"))
                            if pcode == int(reqcode):
                                reqqty -= qty
                            if reqqty <= 0:
                                reqqty = 0
                                break
                        if reqqty <= 0:
                            reqqty = 0
                            break
                    coupon["reqQty"][tag_idx] = reqqty
            else:
                for idx, reqcode in enumerate(coupon["reqProd"]):
                    reqqty = coupon["reqQty"][idx]
                    if reqqty > 0:
                        for line in sale_lines:
                            qty = int(line.get("qty"))
                            pcode = int(line.get("partCode"))
                            if pcode == reqcode:
                                reqqty -= qty
                            if reqqty <= 0:
                                reqqty = 0
                                break
                    coupon["reqQty"][idx] = reqqty
            if coupon["reqType"].endswith("ALL"):
                if not all(q == 0 for q in coupon["reqQty"]):
                    show_messagebox(posid, "$COUPON_PREREQ_FAILED|{}".format(coupon_code), icon="warning")
                    raise Exception("Not all pre-requirements for coupon code [{0}] were satisfied.".format(coupon_code))
            elif coupon["reqType"].endswith("ANY"):
                if not any(q == 0 for q in coupon["reqQty"]):
                    show_messagebox(posid, "$COUPON_PREREQ_FAILED|{}".format(coupon_code), icon="warning")
                    raise Exception("Not all pre-requirements for coupon code [{0}] were satisfied.".format(coupon_code))

            if only_check:
                continue

            message = u""
            show_message = False
            logger.debug(coupon["type"])

            if coupon["type"] in ("ITEM", "ITEM-PROMO"):
                try:
                    promo_price_split = None
                    promo_price_split_residue = D(0)
                    promo_price = D(coupon["promoPrice"]) if "promoPrice" in coupon else None
                    if promo_price is not None:
                        promo_price_split = promo_price / D(coupon["discQty"])
                        promo_price_split = promo_price_split.quantize(D('.01'), decimal.ROUND_HALF_DOWN)
                        if promo_price_split * D(coupon["discQty"]) != promo_price:
                            promo_price_split_residue = promo_price - (promo_price_split * D(coupon["discQty"]))
                    if "discTag" in coupon:
                        discprod = getProductsByTag(posid, coupon["discTag"])
                        coupon["discProd"] = discprod.keys()
                    discounts_to_apply = []
                    firstpromo = True
                    for discpcode in coupon["discProd"]:
                        if coupon["discQty"] <= 0:
                            break
                        for line in sale_lines:
                            if int(line.get("partCode")) == int(discpcode) and int(line.get("qty")) > 0:
                                discQty = coupon["discQty"] if int(line.get("qty")) > coupon["discQty"] else int(line.get("qty"))
                                if int(line.get("qty")) > coupon["discQty"]:
                                    posot.splitOrderLine(posid, line.get("lineNumber"), coupon["discQty"])
                                posot.clearDiscount(discountid=coupon["discountId"], linenumber=line.get("lineNumber"), itemid=line.get("itemId"), level=line.get("level"), partcode=line.get("partCode"))
                                if promo_price is not None:
                                    discountamt = D(discQty) * (D(line.get("unitPrice", "0")) - promo_price_split)
                                else:
                                    discountamt = D(discQty) * D(coupon["discAmt"] if "discAmt" in coupon else ((D(coupon["discRate"]) / D(100)) * D(line.get("unitPrice", "0"))))
                                discounts_to_apply.append({
                                    "discountid": coupon["discountId"],
                                    "discountamt": discountamt,
                                    "linenumber": line.get("lineNumber"),
                                    "itemid": line.get("itemId"),
                                    "level": line.get("level"),
                                    "partcode": line.get("partCode"),
                                    "forcebyitem": 0
                                })
                                message +=  (u"\n" if not firstpromo else "") + (u"%-5s" % str(discQty)) + line.get("productName")
                                firstpromo = False
                                coupon["discQty"] -= discQty
                                show_message = True
                                if coupon["discQty"] <= 0:
                                    break
                    if coupon["discQty"] > 0:
                        show_messagebox(posid, "Unable to distribute the discount for coupon code [{0}].".format(coupon_code), icon="warning")
                        raise Exception("Unable to distribute the discount for coupon code [{0}].".format(coupon_code))
                    sz_discounts_to_apply = len(discounts_to_apply)
                    if promo_price is not None and promo_price_split_residue:
                        discounts_to_apply[-1]["discountamt"] += (promo_price_split_residue * D(-1))
                    idx = 0
                    for d in discounts_to_apply:
                        idx += 1
                        posot.blkopnotify = (idx < sz_discounts_to_apply)
                        posot.applyDiscount(d["discountid"], d["discountamt"], d["linenumber"], d["itemid"], d["level"], d["partcode"], d["forcebyitem"])
                        logger.debug(d["discountamt"])
                except OrderTakerException, e:
                    show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (e.getErrorCode(), e.getErrorDescr()), msgtype="critical")
                    raise
            elif coupon["type"].upper() == "ORDER":
                try:
                    posot = get_posot(model)
                    #discountamt = D(coupon["discAmt"] if "discAmt" in coupon else ((D(coupon["discRate"]) / D(100)) * order_total))

                    posot.blkopnotify = True
                    posot.clearDiscount(coupon["discountId"])
                    posot.blkopnotify = False
                    discountamt = '1.40'
                    posot.applyDiscount(coupon["discountId"], discountamt)
                    show_message = True
                except OrderTakerException, e:

                    show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (e.getErrorCode(), e.getErrorDescr()), msgtype="critical")
                    raise
            if show_message:
                show_messagebox(posid, "$COUPONS_APPLIED|{0}".format(message.replace('\n', ', ').encode('UTF-8')), icon="success")
        except:
            if not only_check:
                try:
                    posot.blkopnotify = False
                    posot.voidLine(posid, line_number)
                except:
                    sys_log_warning("Failed to remove coupon [{0}] product code [{1}] at line [{2}] after a couponp processing error !!!".format(coupon_code, product_code, line_number))
                sys_log_exception("Exception occurred when processing coupon code[{0}] product code [{1}] at line [{2}] after a coupon processing error !!!".format(coupon_code, product_code, line_number))
            else:
                return False

    return True


def promotion(func_or_type):
    """Decorator used to indicate that a function is a discount or promotion script handler
    @param func_or_type: if a function, sets the promotion handler as MANUAL, otherwise set to the given type
    """
    if callable(func_or_type):
        fn = func_or_type
        fn._promotype = MANUAL
        _promotions[fn.func_name] = fn
        return fn

    def wrapper(fn):
        fn._promotype = func_or_type
        _promotions[fn.func_name] = fn
        return fn
    return wrapper


@posactions.action
def runPromotionScript(posid, discountid, *args, **kwargs):
    """
    runPromotionScript(discountid)
    Action used to manually execute the promotion script associated to a discount id.
    @param discountid: Discount identification number
    """
    model = get_model(posid)
    try:
        posot = get_posot(model)
        discounts = etree.XML(posot.getOrderDiscounts(applied=False))
        for discount in discounts.findall("OrderDiscount"):
            if discount.get("discountId") == discountid:
                script = str(discount.get("discountScript"))
                descr = discount.get("discountDescription").encode("UTF-8")
                if script not in _promotions:
                    sys_log_info(
                        "Promotion script [%s] has not been found on POS [%s]" % (script, posid))
                    show_info_message(posid, "$PROMOTION_SCRIPT_NOT_FOUND|%s|%s|%s" % (
                        script, discountid, descr), msgtype="error")
                    return False
                sys_log_info(
                    "Applying promotion script [%s] on POS [%s]" % (script, posid))
                return _promotions[script](posid, discountid, {"model": model}, *args, **kwargs)
        else:
            sys_log_info(
                "Promotion id [%s] has not been found on POS [%s]" % (discountid, posid))
            show_info_message(
                posid, "$INVALID_PROMOTION_ID|%s" % (discountid), msgtype="error")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")
    return False


@posactions.action
def doOpenDiscountType(posid, *args, **kwargs):
    options = ("$EMPLOYEE_DISCOUNT", "$POLICE_AND_FIRE", "$CANCEL")
    select = show_messagebox(
        posid, message="$SELECT_AN_OPTION", title="", icon="question", buttons="|".join(options))
    if select is None or options[select] == "$CANCEL":
        return  # User cancelled, or timeout
    elif options[select] == "$EMPLOYEE_DISCOUNT":
        posactions.doExemptionDiscount(posid, "8", "true")
    elif options[select] == "$POLICE_AND_FIRE":
        posactions.doExemptionDiscount(posid, "9", "true")


@posactions.action
def doOpenCompsType(posid, *args, **kwargs):
    options = ("$EMPLOYEE_MEAL", "$OUR_MISTAKE", "$DIDNT_LIKE", "$MEDIA_PR", "$GUEST_APPRECIATION",
               "$NO_SHOW", "$ON_THE_HOUSE", "$CANCEL")
    select = show_messagebox(
        posid, message="$SELECT_AN_OPTION", title="", icon="question", buttons="|".join(options))
    if select is None or options[select] == "$CANCEL":
        return  # User cancelled, or timeout
    elif options[select] == "$EMPLOYEE_MEAL":
        posactions.doExemptionDiscount(posid, "1", "true")
    elif options[select] == "$OUR_MISTAKE":
        posactions.doExemptionDiscount(posid, "2", "true")
    elif options[select] == "$DIDNT_LIKE":
        posactions.doExemptionDiscount(posid, "3", "true")
    elif options[select] == "$MEDIA_PR":
        posactions.doExemptionDiscount(posid, "4", "true")
    elif options[select] == "$GUEST_APPRECIATION":
        posactions.doExemptionDiscount(posid, "5", "true")
    elif options[select] == "$NO_SHOW":
        posactions.doExemptionDiscount(posid, "6", "true")
    elif options[select] == "$ON_THE_HOUSE":
        posactions.doExemptionDiscount(posid, "7", "true")


@posactions.action
def doOpenDiscount(posid, *args, **kwargs):
    runPromotionScript(posid, "4", input_type="select")


def getProductPrice(posid, itemid):
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
    except:
        sys_log_exception("Unable to acquire product current price")
        pass
    finally:
        if conn:
            conn.close()
    return price


@posactions.action
def doApplicableCoupons(posid, *args, **kwargs):
    model = get_model(posid)
    posot = get_posot(model)
    price_list = get_pricelist(model)
    order = get_current_order(model)

    coupons_available = getAvailableCoupons(posid)
    coupons = [{"code": t["productCode"], "descr": t["couponDescription"], "index": i + 1} for i, t in enumerate(coupons_available)]
    coupons = sorted(coupons, key=lambda c: c["index"])
    coupon_codes = [c["code"] for c in coupons]
    logger.debug(coupon_codes)

    selected_index = show_listbox(
        posid, ["{0} - {1}".format(coupon["index"], coupon["descr"]) for coupon in coupons], message="Selecione o Cupom:"
    )
    if selected_index is None:
        return False
    logger.debug(selected_index)

    coupon = filter(lambda c: c["index"] == selected_index + 1, coupons)
    if not coupon:
        return False
    coupon = coupon[0]
    logger.debug(coupon)


    if check_order_coupons(posid, model=model, coupon_list=[("-1", coupon["code"])], available_coupons=coupons_available, only_check=True):
        try:
            posot.blkopnotify = True
            saleline = posot.doSale(int(posid), itemid="1.{0}".format(coupon["code"]), pricelist=price_list, qtty=1, verifyOption=False, aftertotal="1")
            saleline = etree.XML(saleline)
            order_lines = [(line.get("lineNumber"), line.get("partCode")) for line in order.findall("SaleLine") if int(line.get("qty")) > 0 and int(line.get("level")) == 0 and line.get("partCode") not in coupon_codes]
            order_lines.append((saleline.get("lineNumber"), saleline.get("partCode")))
            return check_order_coupons(posid, model=model, coupon_list=order_lines, available_coupons=coupons_available)
        finally:
            posot.blkopnotify = False

    return False


def getAvailableCoupons(posid):
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
    except:
        sys_log_exception("Unable to parse and build coupons dictionary")
        pass
    finally:
        if conn is not None:
            conn.close()
    return coupons


def getProductsByTag(posid, tag):
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
    except:
        sys_log_exception("Unable to acquire product current price")
        pass
    finally:
        if conn is not None:
            conn.close()
    return products


def getCouponByCode(posid, coupon_code, coupons=[]):
    if not coupons:
        coupons = getAvailableCoupons(posid)
    if coupons:
        coupon = filter(lambda c: True if c.get("code", "") == str(coupon_code) else False, coupons)
        if not coupon:
            return None
        coupon = deepcopy(coupon[0])
        if  not all(k in coupon for k in("type", "discountId", "code", "reqQty", "reqType")) or \
            not any(k in coupon for k in("reqProd", "reqTag")) or \
            not any(k in coupon for k in("discAmt", "discRate", "promoPrice")) or \
            coupon["type"].upper() not in ("ITEM", "ORDER", "ITEM-PROMO") or \
            coupon["reqType"].upper() not in ("ALL", "ANY", "TAG"):
            sys_log_error("Invalid setup of coupon code [{0}]: invalid coupon description".format(coupon["code"]))
            return None
        return coupon
    return None


def getCouponByProductCode(posid, product_code, coupons=[]):
    logger.debug(coupons)
    logger.debug(product_code)
    if not coupons:
        coupons = getAvailableCoupons(posid)
    if coupons:
        coupon = filter(lambda c: True if c.get("productCode", "") == str(product_code) else False, coupons)
        logger.debug(coupon)
        if not coupon:
            return None
        coupon = deepcopy(coupon[0])
        if  not all(k in coupon for k in("type", "discountId", "code", "reqQty", "reqType")) or \
            not any(k in coupon for k in("reqProd", "reqTag")) or \
            not any(k in coupon for k in("discAmt", "discRate", "promoPrice")) or \
            coupon["type"].upper() not in ("ITEM", "ORDER", "ITEM-PROMO") or \
            coupon["reqType"].upper() not in ("ALL", "ANY", "TAG-ALL", "TAG-ANY"):
            sys_log_error("Invalid setup of coupon code [{0}]: invalid coupon description".format(coupon["code"]))
            return None
        logger.debug('chegou aqui')
        return coupon
    return None
