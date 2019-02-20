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
import time
from xml.etree import cElementTree as etree
from decimal import Decimal as D
# Our modules
import pyscripts
import posactions
import persistence
from systools import sys_log_info, sys_log_exception
from sysactions import StopAction, get_model, get_posot, show_info_message, show_messagebox, check_current_order, get_authorization, \
    get_current_order, format_amount, show_keyboard, get_business_period, assert_order_discounts
from posot import OrderTakerException


# Promotion script types
MANUAL = 0          # : Script must be manually executed (thru a button, for example)
ON_TOTAL = 1        # : Script is automatically called when a sale is totalized
ON_ITEMSALE = 2     # : Script is automatically called when an item is sold

# Message-bus context
mbcontext = pyscripts.mbcontext

# Dictionary of promotion scripts
_promotions = {}


#
# Main function (called by pyscripts)
#
def main():
    if not hasattr(posactions.on_before_total, 'callbacks'):
        posactions.on_before_total.callbacks = []
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
        if conn is not None:
            conn.close()
    return price

#
# Discounts and promotion scripts
#


@promotion
def open_discount_type(posid, discountid, *args, **kwargs):
    model = get_model(posid)

    order = get_current_order(model)
    total_amount = D(order.get("totalAmount"))

    if discountid in ('5', '6'):
        amount = ((total_amount * 20) / 100)
        try:
            # Apply (or clear) the discount
            posot = get_posot(model)
            if not get_authorization(posid, min_level=posactions.LEVEL_MANAGER, model=model):
                return
            if float(amount) > 0:
                posot.applyDiscount(discountid, amount)
            else:
                posot.clearDiscount(discountid)
        except OrderTakerException, e:
            show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
                e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@promotion
def open_discount(posid, discountid, extra, *args, **kwargs):
    """
    Implements an open-amount discount. The user just types in the discount amount
    """
    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    # eLanes Ticket #35 (Manager Approval for Open Discounts)
    if not get_authorization(posid, min_level=posactions.LEVEL_MANAGER, model=model):
        return
    input_type = kwargs.get("input_type", "amount")
    if input_type == "select":
        options = ("$AMOUNT", "$PERCENT", "$CANCEL")
        select = show_messagebox(
            posid, message="$SELECT_AN_OPTION", title="", icon="question", buttons="|".join(options))
        if select is None or options[select] == "$CANCEL":
            return  # User cancelled, or timeout
        input_type = "amount" if select == 0 else "percent"
    order = get_current_order(model)
    total_amount = D(order.get("totalAmount"))
    total_tender = D(order.get("totalTender"))
    # Remove items that cannot be discounted from "total_amount"
    conn = persistence.Driver().open(mbcontext)
    cursor = conn.pselect("getValidProductDiscounts", discountId=discountid)
    to_ignore = set([row.get_entry("ItemId")
                     for row in cursor if row.get_entry("Exclude") == 'Y'])
    conn.close()
    for item in order.findall("SaleLine"):
        itemid = str("%s.%s" % (item.get("itemId"), item.get("partCode")))
        if itemid in to_ignore:
            item_price = D(item.get("itemPrice") or "0.00") - \
                D(item.get("itemDiscount") or "0.00")
            total_amount -= item_price
    total_discount = D(order.get("discountAmount"))
    # Calculate the maximum discount amount -> [order total - (total discount
    # - this discount)]
    my_discount = D("0.00")
    discounts = order.get("discountsApplied")
    if discounts:
        discounts = discounts.split(',')
        for disc in discounts:
            id, amt = disc.split(':')
            if id == discountid:
                my_discount = D(amt)
                break
    total_discount -= my_discount
    total_amount -= total_discount
    total_amount -= total_tender
    if total_amount < 0:
        total_amount = D("0.00")

    def fmt(amt):
        return format_amount(model, amt, addsymbol=True)
    if input_type == "amount":
        # input type amount
        amount = show_keyboard(posid, "$ENTER_AMOUNT_MAX_ALLOWED|%s" % fmt(
            total_amount), defvalue="", title="", mask="CURRENCY", numpad=True)
        if not amount:
            return
    else:
        # input type percent
        perc = show_keyboard(
            posid, "$ENTER_PERCENT", defvalue="", title="", mask="NUMBER", numpad=True)
        if not perc:
            return
        if D(perc) <= D("0") or D(perc) > D("100.0"):
            show_info_message(posid, "$INVALID_PERCENT" % (
                fmt(amount), fmt(total_amount)), msgtype="warning")
            return
        if D(perc) == D("100.0"):
            amount = str(total_amount)
        else:
            amount = str((total_amount * D(perc)) / D("100.0"))
    if D(amount) > total_amount:
        # Amount greater than the maximum allowed
        show_info_message(posid, "$AMOUNTS_DIFERENT|%s|%s" %
                          (fmt(amount), fmt(total_amount)), msgtype="warning")
        return
    try:
        # Apply (or clear) the discount
        posot = get_posot(model)
        if float(amount) > 0:
            posot.applyDiscount(discountid, amount)
        else:
            posot.clearDiscount(discountid)
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@promotion
def call_in_code_promo(posid, discountid, extra, *args):
    """
    Free "Single" sandwich promotion (activated by button)
    """
    return _genericFreeItemPromo(posid, discountid, "100081", extra.get("model"), need_nonfree=False, only_once=False)


@promotion
def frosty_tag_promo(posid, discountid, extra, *args):
    """
    Free "Kid Frosty" promotion (activated by button)
    """
    return _genericFreeItemPromo(posid, discountid, "100326,100330,100477", extra.get("model"), need_nonfree=True, only_once=False)


def _genericFreeItemPromo(posid, discountid, free_pcodes, model=None, need_nonfree=True, only_once=True, *args):
    """
    Implements a generic "free item" promotion
    @param posid POS id
    @param discountid discount id
    @param free_pcodes comma-separated list of product codes allowed to be given for free
    @param need_nonfree indicates if the promotion requires other (non-free) items on the order
    @param only_once indicates if the promotion is valid only once per sale
    """
    model = model or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    need_nonfree = str(need_nonfree).lower() == "true"
    only_once = str(only_once).lower() == "true"
    if isinstance(free_pcodes, str):
        free_pcodes = map(int, free_pcodes.split(","))
    # Patterns used to find the discountid on a "discountsApplied" tag
    str_begin = "%s:" % discountid
    str_middle = ",%s:" % discountid

    def has_discount(discountsApplied):
        if not discountsApplied:
            return False
        return (discountsApplied.startswith(str_begin) or str_middle in discountsApplied)

    # Find all level 0 lines
    lines = [line for line in order.findall(
        "SaleLine") if int(line.get("level")) == 0]
    items = [line for line in lines if int(
        line.get("partCode")) in free_pcodes]
    free_items = [
        line for line in items if has_discount(line.get("discountsApplied"))]
    free_qty = sum([int(line.get("qty")) for line in free_items])
    if only_once and free_qty > 0:
        show_messagebox(
            posid, "$THIS_PROMOTION_PER_SALE", icon="warning")
        return
    item_to_give = None
    for line in items:
        if (line not in free_items) and (line.get("qty") > 0):
            item_to_give = line
            break
    if (item_to_give is None):
        show_messagebox(
            posid, "$THERE_NO_INVALID_ITEM_APPLY_PROMOTION", icon="warning")
        return
    if need_nonfree:
        # Check if there is another non-free item
        for line in lines:
            if (line != item_to_give) and (line not in free_items) and (float(line.get("qty")) > 0):
                break
        else:
            show_messagebox(
                posid, "$THIS_PROMOTION_ONLY_APPLIED", icon="warning")
            return
    # We now have everything that is necessary - APPLY!
    try:
        posot = get_posot(model)
        assert_order_discounts(posid, model)
        if float(item_to_give.get("qty")) > 1:
            # We need to split the line first
            posot.splitOrderLine(posid, item_to_give.get("lineNumber"), 1)
        # Apply the discount
        discountamt, linenumber, itemid, level, partcode = map(
            item_to_give.get, ("unitPrice", "lineNumber", "itemId", "level", "partCode"))
        posot.applyDiscount(
            discountid, discountamt, linenumber, itemid, level, partcode)
        message = "$PROMOTION_APPLIED"
        message += "1  " + item_to_give.get("productName") + "\\"
        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


#
# NATIONAL COUPON DROP PROMOTION
# (Expires at Apr/27/2014)
#

def check_coupon_validity(posid, model, order, newdiscountid):
    EXEMPTION_DISCOUNTS = (1, 2, 3)
    COUPON_DISCOUNTS = (10, 11, 15, 16, 17, 24, 27, 28)
    JUNE_CUPON = (30, 31)

    period = get_business_period(model)
    if int(newdiscountid) in COUPON_DISCOUNTS and int(period) > 20140629:
        show_messagebox(
            posid, "$PROMOTION_EXPIRED_JUN_29_2013", icon="warning")
        raise StopAction()

    if int(newdiscountid) in JUNE_CUPON and int(period) > 20140606:
        show_messagebox(
            posid, "$PROMOTION_EXPIRED_JUN_06_2013", icon="warning")
        raise StopAction()

    orderDiscounts = order.get("discountsApplied")
    orderDiscounts = orderDiscounts.split(",") if orderDiscounts else []
    orderDiscounts = [int(d.split(':')[0]) for d in orderDiscounts]
    for discountid in orderDiscounts:
        if discountid in COUPON_DISCOUNTS:
            show_messagebox(
                posid, "$ONLY_ONE_COUPON_TRANSACTION", icon="warning")
            raise StopAction()

    for line in order.findall("SaleLine"):
        discounts = line.get("discountsApplied", "")
        if not discounts:
            continue
        for discount in discounts.split(","):
            discountid = int(discount.split(':')[0])
            if discountid in EXEMPTION_DISCOUNTS:
                show_messagebox(
                    posid, "$ONLY_NOT_APPLY_COUPON_DISCOUNTS", icon="warning")
                raise StopAction()
            if discountid in COUPON_DISCOUNTS:
                show_messagebox(
                    posid, "$ONLY_ONE_COUPON_TRANSACTION", icon="warning")
                raise StopAction()


@promotion
def coupon_free_ciabatta_bacon_cheeseburger(posid, discountid, extra, *args):
    """
#    Free Ciabatta Bacon Cheeseburger with purchase of a small, medium or large
#    fries & drink (20 oz.).

#    If a customer would prefer to purchase a Signature Side vs. a Fry, that is acceptable.
    """
    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    check_coupon_validity(posid, model, order, discountid)
    t = time.localtime()
    t = "%02d%02d" % (t.tm_hour, t.tm_min)
    if t < "1600":
        show_messagebox(
            posid, "$THIS_COUPON_VALID_AFTER_4_00_PM", icon="warning")
        return

    # Lists provided by Scott Weinert
    REQUIRED_SIDE = (100150, 100151, 100152, 100649, 100650, 100652,)
    REQUIRED_DRINK = (100158, 100159, 100160, 100163, 100164, 100165, 100168, 100169, 100170, 100173, 100174, 100175,
                      100178, 100179, 100180, 100188, 100190, 100191, 100192, 100212, 100213, 100214, 100217, 100218,
                      100219, 100222, 100223, 100224, 100227, 100228, 100229, 100254, 100255, 100256, 100259, 100260,
                      100261, 100264, 100265, 100266, 100565, 100566, 100567, 100570, 100571, 100572, 100597, 100598,
                      100599, 100602, 100603, 100604, 100597, 100598, 100599, 100698, 100699, 100700, 100703, 100704,
                      100705, 100708, 100709, 100710,)
    ALLOWED = (100742,)  # Change to Ciabatta code when it`s on database
    required_side_items = []
    required_drink_items = []
    allowed_items = []
    for line in order.findall("SaleLine"):
        if int(line.get("level")) != 0:
            continue
        pcode = int(line.get("partCode"))
        if pcode in REQUIRED_SIDE:
            required_side_items.append(line)
        if pcode in REQUIRED_DRINK:
            required_drink_items.append(line)
        if pcode in ALLOWED:
            allowed_items.append(line)
    if (not allowed_items) or (not required_side_items) or (not required_drink_items):
        show_messagebox(
            posid, "$PLEASE_ADD_DESIRED_ITEMS_ORDER_FIRST", icon="warning")
        return
    item_to_discount = allowed_items[0]
    # Always give the discount in the highest-value item
    for item in allowed_items:
        if (D(item.get("unitPrice")) > D(item_to_discount.get("unitPrice"))):
            item_to_discount = item
    try:
        posot = get_posot(model)
        assert_order_discounts(posid, model)
        if float(item_to_discount.get("qty")) > 1:
            # We need to split the line first
            posot.splitOrderLine(posid, item_to_discount.get("lineNumber"), 1)
        # Apply the discount
        discountamt, linenumber, itemid, level, partcode = map(
            item_to_discount.get, ("unitPrice", "lineNumber", "itemId", "level", "partCode"))
        posot.applyDiscount(
            discountid, discountamt, linenumber, itemid, level, partcode)
        message = "$COUPON_APPLIED_GIVEN_FREE"
        message += "1  " + item_to_discount.get("productName") + "\\"
        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@promotion
def coupon_2chsand(posid, discountid, extra, *args):
    """
    Two Large Chicken Sandwiches for $6.00
        - Spicy, Homemade or Grilled Chicken Fillet
    """
    # Initializations and first validations
    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    check_coupon_validity(posid, model, order, discountid)
    posot = get_posot(model)
    # Promotion configuration
    REQUIRED = {"100120|100121|100122": {"requires": 2.0}, }
    PROMOPRICE = "6.00"
    try:
        # Search for the requirements
        for line in order.findall("SaleLine"):
            if int(line.get("level")) != 0:
                continue
            partCode = line.get("partCode")
            for k in REQUIRED.keys():
                if partCode in k.split('|'):
                    qty = float(line.get("qty", "0"))
                    if qty > 0 and REQUIRED[k]["requires"] > 0:
                        if "lines" not in REQUIRED[k]:
                            REQUIRED[k]["lines"] = []
                        if (REQUIRED[k]["requires"] - qty) < 0:
                            posot.splitOrderLine(
                                posid, line.get("lineNumber"), int(REQUIRED[k]["requires"]))
                            line.set("qty", str(int(REQUIRED[k]["requires"])))
                            REQUIRED[k]["requires"] = 0
                        else:
                            REQUIRED[k]["requires"] -= qty
                        REQUIRED[k]["lines"].append(line)
                    break
        # Validate the promotion and calculate the orinal total amount
        totamt = D("0.00")
        for r in REQUIRED.values():
            if r["requires"] > 0:
                show_messagebox(
                    posid, "$PLEASE_ADD_DESIRED_ITEM_ORDER_FIRST", icon="warning")
                return
            for l in r["lines"]:
                totamt += (D(l.get("unitPrice", "0.00")) * D(l.get("qty")))
        # Check if the discount makes sense
        if totamt < D(PROMOPRICE):
            show_messagebox(
                posid, "$PROMOTIONAL_PRICE_GREATER_SELECTED_TOTAL", icon="warning")
            return
        # Calculate the discount amount
        discamt = totamt - D(PROMOPRICE)
        # Apply the discount on total
        posot.applyDiscount(discountid, str(discamt))
        message = "$COUPON_APPLIED_DISCOUT_AMOUNT|$%s." % (
            str(discamt))
        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@promotion
def coupon_family_meal_deal(posid, discountid, extra, *args):
    """
    $9.99 Family Meal Deal. after 5 pm (includes 2 singles, 2 four piece chicken nuggets, and 4 small fries)
    """
    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    check_coupon_validity(posid, model, order, discountid)
    t = time.localtime()
    t = "%02d%02d" % (t.tm_hour, t.tm_min)
    if t > "0300" and t < "1700":
        show_messagebox(
            posid, "This coupon is only valid between 05:00pm and 03:00am.", icon="warning")
        return

    # Lists provided by Scott Weinert
    REQUIRED_AND = (100080, 100150)
    REQUIRED_OR = (100676, 100114)
    PROMO_PRICE = "9.99"
    count_single = 0
    count_nuggets = 0
    count_fries = 0
    items_total = 0.00
    for line in order.findall("SaleLine"):
        if int(line.get("level")) != 0:
            continue
        pcode = int(line.get("partCode"))
        unitprice = line.get("unitPrice")
        qty = float(line.get("qty"))
        if qty == 0:
            continue
        if pcode in REQUIRED_AND:
            if pcode == 100080:
                if count_single < 2:
                    if qty == 1:
                        items_total += float(unitprice)
                    else:
                        items_total += (float(unitprice) * (2 - count_single))
                count_single += qty
            elif pcode == 100150:
                if count_fries < 4:
                    if qty == 1:
                        items_total += float(unitprice)
                    else:
                        if qty <= (4 - count_fries):
                            items_total += (float(unitprice) * (qty))
                        else:
                            items_total += (float(unitprice) * (4 - count_fries))
                count_fries += qty
        elif pcode in REQUIRED_OR:
            if count_nuggets < 2:
                if qty == 1:
                    items_total += float(unitprice)
                else:
                    items_total += (float(unitprice) * (2 - count_nuggets))
            count_nuggets += qty
    if count_single < 2 or count_nuggets < 2 or count_fries < 4:
        show_messagebox(
            posid, "This coupon is only valid for a 2x Singles w/ 2x 4 Pc Nuggets and 4x Small Fries.\\\\Please add the desired items to the order first.", icon="warning")
        return

    try:
        posot = get_posot(model)
        assert_order_discounts(posid, model)
        # Calculate the discount amount
        discamt = items_total - float(PROMO_PRICE)
        # Apply the discount on total
        posot.applyDiscount(discountid, str(discamt))
        message = "Coupon applied!\\The discount amount was $%s." % (
            str(discamt))
        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@promotion
def coupon_free_frostycone(posid, discountid, extra, *args):
    """
    Free Small Frosty Cone with any purchase
    """
    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    check_coupon_validity(posid, model, order, discountid)

    # Lists provided by Scott Weinert
    ALLOWED = (100711, 100712)
    allowed_items = []
    purchases = 0
    for line in order.findall("SaleLine"):
        if int(line.get("level")) != 0:
            continue
        pcode = int(line.get("partCode"))
        qty = float(line.get("qty"))
        uprice = D(line.get("unitPrice", "0.00"))
        if not uprice.is_zero():
            purchases += qty
        if (pcode in ALLOWED) and qty > 0:
            allowed_items.append(line)
    if not (allowed_items and purchases > 1):
        show_messagebox(
            posid, "This coupon is only valid for a Frosty Cone with any purchase.\\\\" +
            "Please add the desired items to the order first.", icon="warning")
        return
    item_to_discount = allowed_items[0] if allowed_items else None
    for item in allowed_items:
        if (D(item.get("unitPrice")) > D(item_to_discount.get("unitPrice"))):
            item_to_discount = item
    try:
        posot = get_posot(model)
        assert_order_discounts(posid, model)
        if float(item_to_discount.get("qty")) > 1:
            # We need to split the line first
            posot.splitOrderLine(posid, item_to_discount.get("lineNumber"), 1)
        # Apply the discount
        discountamt, linenumber, itemid, level, partcode = map(
            item_to_discount.get, ("unitPrice", "lineNumber", "itemId", "level", "partCode"))
        message = "Coupon applied!\\The following item has been given for free:\\\\"
        posot.applyDiscount(
            discountid, discountamt, linenumber, itemid, level, partcode)
        message += "1  " + item_to_discount.get("productName") + "\\"
        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@promotion
def coupon_2doubles_for_6(posid, discountid, extra, *args):
    """ Purchase 2 Doubles for just $6.00 """

    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    check_coupon_validity(posid, model, order, discountid)

    # Lists provided by Scott Weinert
    ALLOWED = (100082,)
    allowed_items = []
    count_qty = 0
    discount_items = []

    for line in order.findall("SaleLine"):
        if int(line.get("level")) != 0:
            continue
        pcode = int(line.get("partCode"))
        qty = float(line.get("qty"))
        if pcode in ALLOWED and qty > 0:
            allowed_items.append(line)
            count_qty += qty
            if qty == 1:
                discount_items.append(line)
    if count_qty < 2:
        show_messagebox(
            posid, "This coupon is only valid for 2x Dave's Doubles\\\\" +
            "Please add the desired items to the order first.", icon="warning")
        return

    item_to_discount = allowed_items[0]

    for item in allowed_items:
        if int(item.get("qty")) > 1:
            item_to_discount = item

    try:
        posot = get_posot(model)
        assert_order_discounts(posid, model)
        if float(item_to_discount.get("qty")) > 2:
            # We need to split the line first
            posot.splitOrderLine(posid, item_to_discount.get("lineNumber"), 2)
        # Apply discount
        if int(item_to_discount.get("qty")) > 1:
            unitPrice, linenumber, itemid, level, partcode = map(
                item_to_discount.get, ("unitPrice", "lineNumber", "itemId", "level", "partCode"))
            message = "Coupon applied!\\The following item has been given discount:\\\\"
            discountamt = (D(unitPrice) * 2) - D('6.00')
            posot.applyDiscount(
                discountid, discountamt, linenumber, itemid, level, partcode)
            message += "2  " + item_to_discount.get("productName") + "\\"
        else:
            for item in list(discount_items[:2]):
                unitPrice, linenumber, itemid, level, partcode = map(
                    item.get, ("unitPrice", "lineNumber", "itemId", "level", "partCode"))
                message = "Coupon applied!\\The following item has been given discount:\\\\"
                discountamt = (D(unitPrice)) - D('3.00')
                posot.applyDiscount(
                    discountid, discountamt, linenumber, itemid, level, partcode)
                message += "2  " + item_to_discount.get("productName") + "\\"

        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@promotion
def coupon_free_daves_single_cheeseburger(posid, discountid, extra, *args):
    """
    Free Dave's Hot 'N Juicy Single Cheeseburger with purchase of
    small, medium or large fries & drink (20 oz.)

    If a customer would prefer to purchase a Signature Side vs. a Fry, that is acceptable.
    """
    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    check_coupon_validity(posid, model, order, discountid)

    # Lists provided by Scott Weinert
    REQUIRED_SIDE = (100150, 100151, 100152, 100649, 100650, 100652)
    REQUIRED_DRINK = (100158, 100159, 100160, 100163, 100164, 100165, 100168, 100169, 100170, 100173, 100174, 100175,
                      100178, 100179, 100180, 100188, 100190, 100191, 100192, 100212, 100213, 100214, 100217, 100218,
                      100219, 100222, 100223, 100224, 100227, 100228, 100229, 100254, 100255, 100256, 100259, 100260,
                      100261, 100264, 100265, 100266, 100565, 100566, 100567, 100570, 100571, 100572, 100597, 100598,
                      100599, 100602, 100603, 100604, 100597, 100598, 100599, 100698, 100699, 100700, 100703, 100704,
                      100705, 100708, 100709, 100710,)
    ALLOWED = (100080,)
    DISCOUNT_ALLOWED = []  # (100082,100084)
    required_side_items = []
    required_drink_items = []
    allowed_items = []
    for line in order.findall("SaleLine"):
        if int(line.get("level")) != 0:
            continue
        pcode = int(line.get("partCode"))
        qty = float(line.get("qty"))
        if pcode in REQUIRED_SIDE and qty > 0:
            required_side_items.append(line)
        if pcode in REQUIRED_DRINK and qty > 0:
            required_drink_items.append(line)
        if (pcode in ALLOWED or pcode in DISCOUNT_ALLOWED) and qty > 0:
            allowed_items.append(line)
    if (not allowed_items) or (not required_side_items) or (not required_drink_items):
        show_messagebox(
            posid, "This coupon is only valid for a Dave's Hot 'N Juicy Single Cheeseburger\\with purchase of fries & drink (20 oz.)\\\\Please add the desired items to the order first.", icon="warning")
        return
    item_to_discount = allowed_items[0]
    # Always give the discount in the highest-value item
    for item in allowed_items:
        if (D(item.get("unitPrice")) > D(item_to_discount.get("unitPrice"))):
            item_to_discount = item
    try:
        posot = get_posot(model)
        assert_order_discounts(posid, model)
        if float(item_to_discount.get("qty")) > 1:
            # We need to split the line first
            posot.splitOrderLine(posid, item_to_discount.get("lineNumber"), 1)
        # Apply the discount
        unitPrice, linenumber, itemid, level, partcode = map(
            item_to_discount.get, ("unitPrice", "lineNumber", "itemId", "level", "partCode"))
        message = "Coupon applied!\\The following item has been given for free:\\\\"
        if (int(item_to_discount.get("partCode")) in DISCOUNT_ALLOWED):
            discountamt = getProductPrice(
                posid, "50000.%d" % (ALLOWED[0]))  # "3.49"
            message = "Coupon applied!\\The following item has been given a discount:\\\\"
        else:
            discountamt = unitPrice
        posot.applyDiscount(
            discountid, discountamt, linenumber, itemid, level, partcode)
        message += "1  " + item_to_discount.get("productName") + "\\"
        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@promotion
def coupon_free_ch_sandwich(posid, discountid, extra, *args):
    """
    Free Large Chicken Sandwich (Spicy, Homestyle, or Grilled Chicken) with purchase of
    small, medium or large fries & drink (20 oz.)

    If a customer would prefer to purchase a Signature Side vs. a Fry, that is acceptable.
    """
    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    check_coupon_validity(posid, model, order, discountid)

    # Lists provided by Scott Weinert
    REQUIRED_SIDE = (100150, 100151, 100152, 100649, 100650, 100652)
    REQUIRED_DRINK = (100158, 100159, 100160, 100163, 100164, 100165, 100168, 100169, 100170, 100173, 100174, 100175,
                      100178, 100179, 100180, 100188, 100190, 100191, 100192, 100212, 100213, 100214, 100217, 100218,
                      100219, 100222, 100223, 100224, 100227, 100228, 100229, 100254, 100255, 100256, 100259, 100260,
                      100261, 100264, 100265, 100266, 100565, 100566, 100567, 100570, 100571, 100572, 100597, 100598,
                      100599, 100602, 100603, 100604, 100597, 100598, 100599, 100698, 100699, 100700, 100703, 100704,
                      100705, 100708, 100709, 100710,)
    ALLOWED = (100120, 100121, 100122,)
    DISCOUNT_ALLOWED = (100537,)
    required_side_items = []
    required_drink_items = []
    allowed_items = []
    for line in order.findall("SaleLine"):
        if int(line.get("level")) != 0:
            continue
        pcode = int(line.get("partCode"))
        qty = float(line.get("qty"))
        if pcode in REQUIRED_SIDE and qty > 0:
            required_side_items.append(line)
        if pcode in REQUIRED_DRINK and qty > 0:
            required_drink_items.append(line)
        if (pcode in ALLOWED or pcode in DISCOUNT_ALLOWED) and qty > 0:
            allowed_items.append(line)
    if (not allowed_items) or (not required_side_items) or (not required_drink_items):
        show_messagebox(
            posid, "This coupon is only valid for a Large Chicken Sandwich (Spicy, Homestyle or Grilled) with purchase of\\fries & drink (20 oz.)\\A Signature Side vs. a Fry is also accepted.\\\\Please add the desired items to the order first.", icon="warning")
        return
    item_to_discount = allowed_items[0]
    # Always give the discount in the highest-value item
    for item in allowed_items:
        if (D(item.get("unitPrice")) > D(item_to_discount.get("unitPrice"))):
            item_to_discount = item
    try:
        posot = get_posot(model)
        assert_order_discounts(posid, model)
        if float(item_to_discount.get("qty")) > 1:
            # We need to split the line first
            posot.splitOrderLine(posid, item_to_discount.get("lineNumber"), 1)
        # Apply the discount
        unitPrice, linenumber, itemid, level, partcode = map(
            item_to_discount.get, ("unitPrice", "lineNumber", "itemId", "level", "partCode"))
        message = "Coupon applied!\\The following item has been given for free:\\\\"
        if (int(item_to_discount.get("partCode")) in DISCOUNT_ALLOWED):
            discountamt = getProductPrice(
                posid, "50000.%d" % (ALLOWED[0]))  # "4.09"
            message = "Coupon applied!\\The following item has been given a discount:\\\\"
        else:
            discountamt = unitPrice
        posot.applyDiscount(
            discountid, discountamt, linenumber, itemid, level, partcode)
        message += "1  " + item_to_discount.get("productName") + "\\"
        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@promotion
def coupon_free_flatbread_sandwich(posid, discountid, extra, *args):
    """
    Free Flatbread Chicken Grillet with purchase of
    small, medium or large fries & drink (20 oz.)

    If a customer would prefer to purchase a Signature Side vs. a Fry, that is acceptable.
    """
    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    check_coupon_validity(posid, model, order, discountid)

    # Lists provided by Scott Weinert
    REQUIRED_SIDE = (100150, 100151, 100152, 100649, 100650, 100652)
    REQUIRED_DRINK = (100158, 100159, 100160, 100163, 100164, 100165, 100168, 100169, 100170, 100173, 100174, 100175,
                      100178, 100179, 100180, 100188, 100190, 100191, 100192, 100212, 100213, 100214, 100217, 100218,
                      100219, 100222, 100223, 100224, 100227, 100228, 100229, 100254, 100255, 100256, 100259, 100260,
                      100261, 100264, 100265, 100266, 100565, 100566, 100567, 100570, 100571, 100572, 100597, 100598,
                      100599, 100602, 100603, 100604, 100597, 100598, 100599, 100698, 100699, 100700, 100703, 100704,
                      100705, 100708, 100709, 100710,)
    ALLOWED = (100692, 100688,)
    required_side_items = []
    required_drink_items = []
    allowed_items = []
    for line in order.findall("SaleLine"):
        if int(line.get("level")) != 0:
            continue
        pcode = int(line.get("partCode"))
        qty = float(line.get("qty"))
        if pcode in REQUIRED_SIDE and qty > 0:
            required_side_items.append(line)
        if pcode in REQUIRED_DRINK and qty > 0:
            required_drink_items.append(line)
        if pcode in ALLOWED and qty > 0:
            allowed_items.append(line)
    if (not allowed_items) or (not required_side_items) or (not required_drink_items):
        show_messagebox(
            posid, "This coupon is only valid for a Flatbread Grilled Chicken with purchase of fries & drink (20 oz.)\\\\" +
            "Please add the desired items to the order first.", icon="warning")
        return
    item_to_discount = allowed_items[0]
    # Always give the discount in the highest-value item
    for item in allowed_items:
        if (D(item.get("unitPrice")) > D(item_to_discount.get("unitPrice"))):
            item_to_discount = item
    try:
        posot = get_posot(model)
        assert_order_discounts(posid, model)
        if float(item_to_discount.get("qty")) > 1:
            # We need to split the line first
            posot.splitOrderLine(posid, item_to_discount.get("lineNumber"), 1)
        # Apply the discount
        unitPrice, linenumber, itemid, level, partcode = map(
            item_to_discount.get, ("unitPrice", "lineNumber", "itemId", "level", "partCode"))
        message = "Coupon applied!\\The following item has been given for free:\\\\"
        discountamt = unitPrice
        posot.applyDiscount(
            discountid, discountamt, linenumber, itemid, level, partcode)
        message += "1  " + item_to_discount.get("productName") + "\\"
        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@promotion
def coupon_free_smchili(posid, discountid, extra, *args):
    """
    Free Small Chili with any purchase
    """
    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    check_coupon_validity(posid, model, order, discountid)

    # Lists provided by Scott Weinert
    ALLOWED = (100298,)
    DISCOUNT_ALLOWED = (100299,)
    allowed_items = []
    purchases = 0
    for line in order.findall("SaleLine"):
        if int(line.get("level")) != 0:
            continue
        pcode = int(line.get("partCode"))
        qty = float(line.get("qty"))
        uprice = D(line.get("unitPrice", "0.00"))
        if not uprice.is_zero():
            purchases += qty
        if (pcode in ALLOWED or pcode in DISCOUNT_ALLOWED) and qty > 0:
            allowed_items.append(line)
    if not (allowed_items and purchases > 1):
        show_messagebox(
            posid, "This coupon is only valid for a Small Chili with any purchase.\\\\" +
            "Please add the desired items to the order first.", icon="warning")
        return
    item_to_discount = allowed_items[0] if allowed_items else None
    for item in allowed_items:
        if int(item.get("partCode")) in ALLOWED:
            item_to_discount = item
            break
    try:
        posot = get_posot(model)
        assert_order_discounts(posid, model)
        if float(item_to_discount.get("qty")) > 1:
            # We need to split the line first
            posot.splitOrderLine(posid, item_to_discount.get("lineNumber"), 1)
        # Apply the discount
        discountamt, linenumber, itemid, level, partcode = map(
            item_to_discount.get, ("unitPrice", "lineNumber", "itemId", "level", "partCode"))
        if int(partcode) in DISCOUNT_ALLOWED:
            discountamt = getProductPrice(
                posid, "50000.%d" % (ALLOWED[0]))  # "1.39"
            message = "Coupon applied!\\The following item has been given a $%s discount:\\\\" % (
                discountamt)
        else:
            message = "Coupon applied!\\The following item has been given for free:\\\\"
        posot.applyDiscount(
            discountid, discountamt, linenumber, itemid, level, partcode)
        message += "1  " + item_to_discount.get("productName") + "\\"
        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@promotion
def coupon_199_off_kids_meal(posid, discountid, extra, *args):
    """
    $1.99 Kids Meal (limit <DISCOUNT_LIMIT>)
    """
    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    check_coupon_validity(posid, model, order, discountid)

    # Lists provided by Scott Weinert
    ALLOWED = (100347, 100348, 100349, 100350, 100651, 100713)
    DISCOUNTID = 9
    DISCOUNT_LIMIT = 1
    discounted_items = []
    allowed_items = []
    for line in order.findall("SaleLine"):
        if int(line.get("level")) != 0:
            continue
        pcode = int(line.get("partCode"))
        qty = float(line.get("qty"))
        discounts = line.get("discountsApplied")
        discounts = list(
            int(d.split(':')[0]) for d in discounts.split(',')) if discounts else []
        if pcode in ALLOWED and qty > 0:
            if DISCOUNTID in discounts:
                discounted_items.append(line)
            else:
                allowed_items.append(line)
    if ((len(discounted_items) + 1) > DISCOUNT_LIMIT):
        show_messagebox(posid, "You can purchase a maximum of %d Kid's Meal with this coupon." % (
            DISCOUNT_LIMIT), icon="warning")
        return
    if (not allowed_items):
        show_messagebox(
            posid, "This coupon is only valid for a Kid's Meal with any purchase.\\\\" +
            "Please add the desired items to the order first.", icon="warning")
        return
    item_to_discount = allowed_items[0]
    # Always give the discount in the highest-value item
    for item in allowed_items:
        if (D(item.get("unitPrice")) > D(item_to_discount.get("unitPrice"))):
            item_to_discount = item
    try:
        posot = get_posot(model)
        assert_order_discounts(posid, model)
        if float(item_to_discount.get("qty")) > 1:
            # We need to split the line first
            posot.splitOrderLine(posid, item_to_discount.get("lineNumber"), 1)
        # Apply the discount
        unitPrice, linenumber, itemid, level, partcode = map(
            item_to_discount.get, ("unitPrice", "lineNumber", "itemId", "level", "partCode"))
        discountamt = D(unitPrice) - D("1.99")
        posot.applyDiscount(
            discountid, discountamt, linenumber, itemid, level, partcode)
        message = "Coupon applied!\\The following item has been given for $1.99:\\\\"
        message += "1  " + item_to_discount.get("productName") + "\\"
        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@promotion
def coupon_free_fries_drink(posid, discountid, extra, *args):
    """
    Free small fries & drink with purchase of a Flatbread Grilled Chicken
    """
    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    check_coupon_validity(posid, model, order, discountid)

    # Lists provided by Scott Weinert
    REQUIRED = (100692, 100688,)
    ALLOWED_DRINKS = (100158, 100163, 100168, 100173, 100178, 100188, 100212, 100217, 100222,
                      100227, 100237, 100254, 100259, 100264, 100435, 100474, 100565, 100570, 100597, 100602,)
    DISCOUNT_ALLOWED_DRINKS = (100159, 100160, 100164, 100165, 100169, 100170, 100174, 100175, 100179, 100180, 100213,
                               100214, 100218, 100219, 100223, 100224, 100228, 100229, 100238, 100239, 100255, 100256,
                               100260, 100261, 100265, 100266, 100436, 100475, 100476, 100566, 100567, 100571, 100572,
                               100598, 100599, 100603, 100604, 100597, 100598, 100599, 100698, 100699, 100700, 100703,
                               100704, 100705, 100708, 100709, 100710,)
    ALLOWED_SIDES = (100150,)
    DISCOUNT_ALLOWED_SIDES = (100151, 100152,)
    required_items = []
    allowed_drinks = []
    allowed_sides = []
    for line in order.findall("SaleLine"):
        if int(line.get("level")) != 0:
            continue
        pcode = int(line.get("partCode"))
        qty = float(line.get("qty"))
        if pcode in REQUIRED and qty > 0:
            required_items.append(line)
        if (pcode in ALLOWED_DRINKS or pcode in DISCOUNT_ALLOWED_DRINKS) and qty > 0:
            allowed_drinks.append(line)
        if (pcode in ALLOWED_SIDES or pcode in DISCOUNT_ALLOWED_SIDES) and qty > 0:
            allowed_sides.append(line)
    if (not required_items) or (not allowed_drinks) or (not allowed_sides):
        show_messagebox(
            posid, "This coupon is only valid for a small fries and drink with purchase of a 100% North Pacific Cod Fillet Sandwich.\\\\" +
            "Please add the desired items to the order first.", icon="warning")
        return
    drink_to_discount = allowed_drinks[0]
    side_to_discount = allowed_sides[0]
    # Always give the discount in the highest-value item
    for item in allowed_drinks:
        if (D(item.get("unitPrice")) > D(drink_to_discount.get("unitPrice"))):
            drink_to_discount = item
    for item in allowed_sides:
        if (D(item.get("unitPrice")) > D(side_to_discount.get("unitPrice"))):
            side_to_discount = item
    try:
        posot = get_posot(model)
        assert_order_discounts(posid, model)
        if float(drink_to_discount.get("qty")) > 1:
            # We need to split the line first
            posot.splitOrderLine(posid, drink_to_discount.get("lineNumber"), 1)
        if float(side_to_discount.get("qty")) > 1:
            # We need to split the line first
            posot.splitOrderLine(posid, side_to_discount.get("lineNumber"), 1)
        # Apply the discount
        message = "Coupon applied!\\The following item has been given for free:\\\\"
        unitPrice, linenumber, itemid, level, partcode = map(
            drink_to_discount.get, ("unitPrice", "lineNumber", "itemId", "level", "partCode"))
        if (int(drink_to_discount.get("partCode")) in DISCOUNT_ALLOWED_DRINKS):
            discountamt = getProductPrice(
                posid, "50000.%d" % (ALLOWED_DRINKS[0]))  # "1.49"
            message = "Coupon applied!\\The following item has been given a discount:\\\\"
        else:
            discountamt = unitPrice
        posot.applyDiscount(
            discountid, discountamt, linenumber, itemid, level, partcode)
        unitPrice, linenumber, itemid, level, partcode = map(
            side_to_discount.get, ("unitPrice", "lineNumber", "itemId", "level", "partCode"))
        if (int(side_to_discount.get("partCode")) in DISCOUNT_ALLOWED_SIDES):
            discountamt = getProductPrice(
                posid, "50000.%d" % (ALLOWED_SIDES[0]))  # "1.39"
            message = "Coupon applied!\\The following item has been given a discount:\\\\"
        else:
            discountamt = unitPrice
        posot.applyDiscount(
            discountid, discountamt, linenumber, itemid, level, partcode)
        message += "1  " + drink_to_discount.get("productName") + "\\"
        message += "1  " + side_to_discount.get("productName") + "\\"
        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@promotion
def coupon_free_chili_cheese_fries(posid, discountid, extra, *args):
    """
    Free Chili Cheese Fries with any purchase
    """
    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    check_coupon_validity(posid, model, order, discountid)

    # Lists provided by Scott Weinert
    ALLOWED = (100652,)
    DISCOUNT_ALLOWED_DRINKS = (100158, 100163, 100168, 100173, 100178, 100188, 100212, 100217, 100222, 100227, 100237,
                               100254, 100259, 100264, 100435, 100474, 100565, 100570, 100597, 100602, 100159, 100160,
                               100164, 100165, 100169, 100170, 100174, 100175, 100179, 100180, 100213, 100214, 100218,
                               100219, 100223, 100224, 100228, 100229, 100238, 100239, 100255, 100256, 100260, 100261,
                               100265, 100266, 100436, 100475, 100476, 100566, 100567, 100571, 100572, 100598, 100599,
                               100603, 100604, 100597, 100598, 100599, 100698, 100699, 100700, 100703, 100704, 100705,
                               100708, 100709, 100710,)
    DISCOUNT_ALLOWED_SIDES = (100150, 100151, 100152,)
    allowed_items = []
    discount_allowed_drinks = []
    discount_allowed_sides = []
    purchases = 0
    for line in order.findall("SaleLine"):
        if int(line.get("level")) != 0:
            continue
        pcode = int(line.get("partCode"))
        qty = float(line.get("qty"))
        uprice = D(line.get("unitPrice", "0.00"))
        if not uprice.is_zero():
            purchases += qty
        if pcode in ALLOWED and qty > 0:
            allowed_items.append(line)
        if pcode in DISCOUNT_ALLOWED_DRINKS and qty > 0:
            discount_allowed_drinks.append(line)
        if pcode in DISCOUNT_ALLOWED_SIDES and qty > 0:
            discount_allowed_sides.append(line)
    if not (allowed_items and purchases > 1) and not (discount_allowed_drinks and discount_allowed_sides and purchases > 2):
        show_messagebox(
            posid, "This coupon is only valid for a chili cheese fries with any purchase.\\\\" +
            "Please add the desired items to the order first.", icon="warning")
        return
    item_to_discount = allowed_items[0] if allowed_items else None
    for item in allowed_items:
        if (D(item.get("unitPrice")) > D(item_to_discount.get("unitPrice"))):
            item_to_discount = item
    drink_to_discount = discount_allowed_drinks[
        0] if discount_allowed_drinks else None
    for item in discount_allowed_drinks:
        if (D(item.get("unitPrice")) > D(drink_to_discount.get("unitPrice"))):
            drink_to_discount = item
    side_to_discount = discount_allowed_sides[
        0] if discount_allowed_sides else None
    for item in discount_allowed_sides:
        if (D(item.get("unitPrice")) > D(side_to_discount.get("unitPrice"))):
            side_to_discount = item

    # check if the coupon is being used to give a discount for a drink and a
    # side first
    do_drink_side_discount = (item_to_discount is None)

    try:
        posot = get_posot(model)
        assert_order_discounts(posid, model)
        if do_drink_side_discount:
            message = "Coupon applied!\\The following items has been given a discount:\\\\"
            # D("2.49") # chili fries unit price
            discountamt = D(getProductPrice(posid, "50000.%d" % (ALLOWED[0])))
            item_to_discount = [drink_to_discount, side_to_discount, ]
            for item in item_to_discount:
                unitPrice, linenumber, itemid, level, partcode = map(
                    item.get, ("unitPrice", "lineNumber", "itemId", "level", "partCode"))
                if discountamt > D("0.00"):
                    posot.applyDiscount(discountid, unitPrice if discountamt >= D(
                        unitPrice) else str(discountamt), linenumber, itemid, level, partcode)
                    discountamt -= D(unitPrice)
                    message += "1  " + item.get("productName") + "\\"
        else:
            if float(item_to_discount.get("qty")) > 1:
                # We need to split the line first
                posot.splitOrderLine(
                    posid, item_to_discount.get("lineNumber"), 1)
            # Apply the discount
            discountamt, linenumber, itemid, level, partcode = map(
                item_to_discount.get, ("unitPrice", "lineNumber", "itemId", "level", "partCode"))
            posot.applyDiscount(
                discountid, discountamt, linenumber, itemid, level, partcode)
            message = "Coupon applied!\\The following item has been given for free:\\\\"
            message += "1  " + item_to_discount.get("productName") + "\\"
        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@promotion
def coupon_free_fries_drink2(posid, discountid, extra, *args):
    """
    Free Small Fries & Drink with purchase of Mozzarella Chicken Supreme sandwich.
    """
    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    check_coupon_validity(posid, model, order, discountid)

    # Lists provided by Scott Weinert
    REQUIRED = (100672,)
    ALLOWED_DRINKS = (100158, 100163, 100168, 100173, 100178, 100188, 100212, 100217, 100222,
                      100227, 100237, 100254, 100259, 100264, 100435, 100474, 100565, 100570, 100597, 100602,)
    DISCOUNT_ALLOWED_DRINKS = (100159, 100160, 100164, 100165, 100169, 100170, 100174, 100175, 100179, 100180, 100213,
                               100214, 100218, 100219, 100223, 100224, 100228, 100229, 100238, 100239, 100255, 100256,
                               100260, 100261, 100265, 100266, 100436, 100475, 100476, 100566, 100567, 100571, 100572,
                               100598, 100599, 100603, 100604, 100597, 100598, 100599, 100698, 100699, 100700, 100703,
                               100704, 100705, 100708, 100709, 100710,)
    ALLOWED_SIDES = (100150,)
    DISCOUNT_ALLOWED_SIDES = (100151, 100152,)
    required_items = []
    allowed_drinks = []
    allowed_sides = []
    for line in order.findall("SaleLine"):
        if int(line.get("level")) != 0:
            continue
        pcode = int(line.get("partCode"))
        qty = float(line.get("qty"))
        if pcode in REQUIRED and qty > 0:
            required_items.append(line)
        if (pcode in ALLOWED_DRINKS or pcode in DISCOUNT_ALLOWED_DRINKS) and qty > 0:
            allowed_drinks.append(line)
        if (pcode in ALLOWED_SIDES or pcode in DISCOUNT_ALLOWED_SIDES) and qty > 0:
            allowed_sides.append(line)
    if (not required_items) or (not allowed_drinks) or (not allowed_sides):
        show_messagebox(
            posid, "This coupon is only valid for a small fries and drink\\" +
            "with purchase of a Asiago Ranch Chicken Club Sandwich.\\\\" +
            "Please add the desired items to the order first.", icon="warning")
        return
    drink_to_discount = allowed_drinks[0]
    side_to_discount = allowed_sides[0]
    # Always give the discount in the highest-value item
    for item in allowed_drinks:
        if (D(item.get("unitPrice")) > D(drink_to_discount.get("unitPrice"))):
            drink_to_discount = item
    for item in allowed_sides:
        if (D(item.get("unitPrice")) > D(side_to_discount.get("unitPrice"))):
            side_to_discount = item
    try:
        posot = get_posot(model)
        assert_order_discounts(posid, model)
        if float(drink_to_discount.get("qty")) > 1:
            # We need to split the line first
            posot.splitOrderLine(posid, drink_to_discount.get("lineNumber"), 1)
        if float(side_to_discount.get("qty")) > 1:
            # We need to split the line first
            posot.splitOrderLine(posid, side_to_discount.get("lineNumber"), 1)
        # Apply the discount
        message = "Coupon applied!\\The following item has been given for free:\\\\"
        unitPrice, linenumber, itemid, level, partcode = map(
            drink_to_discount.get, ("unitPrice", "lineNumber", "itemId", "level", "partCode"))
        if (int(drink_to_discount.get("partCode")) in DISCOUNT_ALLOWED_DRINKS):
            discountamt = getProductPrice(
                posid, "50000.%d" % (ALLOWED_DRINKS[0]))  # "1.49"
            message = "Coupon applied!\\The following item has been given a discount:\\\\"
        else:
            discountamt = unitPrice
        posot.applyDiscount(
            discountid, discountamt, linenumber, itemid, level, partcode)
        unitPrice, linenumber, itemid, level, partcode = map(
            side_to_discount.get, ("unitPrice", "lineNumber", "itemId", "level", "partCode"))
        if (int(side_to_discount.get("partCode")) in DISCOUNT_ALLOWED_SIDES):
            discountamt = getProductPrice(
                posid, "50000.%d" % (ALLOWED_SIDES[0]))  # "1.39"
            message = "Coupon applied!\\The following item has been given a discount:\\\\"
        else:
            discountamt = unitPrice
        posot.applyDiscount(
            discountid, discountamt, linenumber, itemid, level, partcode)
        message += "1  " + drink_to_discount.get("productName") + "\\"
        message += "1  " + side_to_discount.get("productName") + "\\"
        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@promotion
def coupon_free_fries_drink3(posid, discountid, extra, *args):
    """
    Free small fries & drink with purchase of a Baconator or Son of Baconator.
    """
    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    check_coupon_validity(posid, model, order, discountid)

    # Lists provided by Scott Weinert
    REQUIRED = (100106, 100485, 100489, 100656,)
    ALLOWED_DRINKS = (100158, 100163, 100168, 100173, 100178, 100188, 100212, 100217, 100222,
                      100227, 100237, 100254, 100259, 100264, 100435, 100474, 100565, 100570, 100597, 100602,)
    DISCOUNT_ALLOWED_DRINKS = (100159, 100160, 100164, 100165, 100169, 100170, 100174, 100175, 100179, 100180, 100213,
                               100214, 100218, 100219, 100223, 100224, 100228, 100229, 100238, 100239, 100255, 100256,
                               100260, 100261, 100265, 100266, 100436, 100475, 100476, 100566, 100567, 100571, 100572,
                               100598, 100599, 100603, 100604, 100597, 100598, 100599, 100698, 100699, 100700, 100703,
                               100704, 100705, 100708, 100709, 100710,)
    ALLOWED_SIDES = (100150,)
    DISCOUNT_ALLOWED_SIDES = (100151, 100152,)
    required_items = []
    allowed_drinks = []
    allowed_sides = []
    for line in order.findall("SaleLine"):
        if int(line.get("level")) != 0:
            continue
        pcode = int(line.get("partCode"))
        if pcode in REQUIRED:
            required_items.append(line)
        if pcode in ALLOWED_DRINKS or pcode in DISCOUNT_ALLOWED_DRINKS:
            allowed_drinks.append(line)
        if pcode in ALLOWED_SIDES or pcode in DISCOUNT_ALLOWED_SIDES:
            allowed_sides.append(line)
    if (not required_items) or (not allowed_drinks) or (not allowed_sides):
        show_messagebox(
            posid, "This coupon is only valid for a small fries and drink\\" +
            "with purchase of a Baconator or a Son of Baconator.\\\\" +
            "Please add the desired items to the order first.", icon="warning")
        return
    drink_to_discount = allowed_drinks[0]
    side_to_discount = allowed_sides[0]
    # Always give the discount in the highest-value item
    for item in allowed_drinks:
        if item in ALLOWED_DRINKS:
            drink_to_discount = item
    for item in allowed_sides:
        if item in ALLOWED_SIDES:
            side_to_discount = item
    try:
        posot = get_posot(model)
        assert_order_discounts(posid, model)
        if float(drink_to_discount.get("qty")) > 1:
            # We need to split the line first
            posot.splitOrderLine(posid, drink_to_discount.get("lineNumber"), 1)
        if float(side_to_discount.get("qty")) > 1:
            # We need to split the line first
            posot.splitOrderLine(posid, side_to_discount.get("lineNumber"), 1)
        # Apply the discount
        message = "Coupon applied!\\The following item has been given for free:\\\\"
        unitPrice, linenumber, itemid, level, partcode = map(
            drink_to_discount.get, ("unitPrice", "lineNumber", "itemId", "level", "partCode"))
        if (int(drink_to_discount.get("partCode")) in DISCOUNT_ALLOWED_DRINKS):
            discountamt = getProductPrice(
                posid, "50000.%d" % (ALLOWED_DRINKS[0]))  # "1.49"
            message = "Coupon applied!\\The following item has been given a discount:\\\\"
        else:
            discountamt = unitPrice
        posot.applyDiscount(
            discountid, discountamt, linenumber, itemid, level, partcode)
        unitPrice, linenumber, itemid, level, partcode = map(
            side_to_discount.get, ("unitPrice", "lineNumber", "itemId", "level", "partCode"))
        if (int(side_to_discount.get("partCode")) in DISCOUNT_ALLOWED_SIDES):
            discountamt = getProductPrice(
                posid, "50000.%d" % (ALLOWED_SIDES[0]))  # "1.39"
            message = "Coupon applied!\\The following item has been given a discount:\\\\"
        else:
            discountamt = unitPrice
        posot.applyDiscount(
            discountid, discountamt, linenumber, itemid, level, partcode)
        message += "1  " + drink_to_discount.get("productName") + "\\"
        message += "1  " + side_to_discount.get("productName") + "\\"
        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@promotion
def coupon_free_fries_drink4(posid, discountid, extra, *args):
    """
    Free small fries & drink with purchase of a Asiago Ranch Chicken Club
    """
    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    check_coupon_validity(posid, model, order, discountid)

    # Lists provided by Scott Weinert
    REQUIRED = (100537,)
    ALLOWED_DRINKS = (100158, 100163, 100168, 100173, 100178, 100188, 100212, 100217, 100222,
                      100227, 100237, 100254, 100259, 100264, 100435, 100474, 100565, 100570, 100597, 100602,)
    DISCOUNT_ALLOWED_DRINKS = (100159, 100160, 100164, 100165, 100169, 100170, 100174, 100175, 100179, 100180, 100213,
                               100214, 100218, 100219, 100223, 100224, 100228, 100229, 100238, 100239, 100255, 100256,
                               100260, 100261, 100265, 100266, 100436, 100475, 100476, 100566, 100567, 100571, 100572,
                               100598, 100599, 100603, 100604, 100597, 100598, 100599, 100698, 100699, 100700, 100703,
                               100704, 100705, 100708, 100709, 100710,)
    ALLOWED_SIDES = (100150,)
    DISCOUNT_ALLOWED_SIDES = (100151, 100152,)
    required_items = []
    allowed_drinks = []
    allowed_sides = []
    for line in order.findall("SaleLine"):
        if int(line.get("level")) != 0:
            continue
        pcode = int(line.get("partCode"))
        qty = float(line.get("qty"))
        if pcode in REQUIRED and qty > 0:
            required_items.append(line)
        if (pcode in ALLOWED_DRINKS or pcode in DISCOUNT_ALLOWED_DRINKS) and qty > 0:
            allowed_drinks.append(line)
        if (pcode in ALLOWED_SIDES or pcode in DISCOUNT_ALLOWED_SIDES) and qty > 0:
            allowed_sides.append(line)
    if (not required_items) or (not allowed_drinks) or (not allowed_sides):
        show_messagebox(
            posid, "This coupon is only valid for a small fries and drink with purchase of a Asiago Ranch Chicken Club.\\\\" +
            "Please add the desired items to the order first.", icon="warning")
        return
    drink_to_discount = allowed_drinks[0]
    side_to_discount = allowed_sides[0]
    # Always give the discount in the highest-value item
    for item in allowed_drinks:
        if item in ALLOWED_DRINKS:
            drink_to_discount = item
    for item in allowed_sides:
        if item in ALLOWED_SIDES:
            side_to_discount = item
    try:
        posot = get_posot(model)
        assert_order_discounts(posid, model)
        if float(drink_to_discount.get("qty")) > 1:
            # We need to split the line first
            posot.splitOrderLine(posid, drink_to_discount.get("lineNumber"), 1)
        if float(side_to_discount.get("qty")) > 1:
            # We need to split the line first
            posot.splitOrderLine(posid, side_to_discount.get("lineNumber"), 1)
        # Apply the discount
        message = "Coupon applied!\\The following item has been given for free:\\\\"
        unitPrice, linenumber, itemid, level, partcode = map(
            drink_to_discount.get, ("unitPrice", "lineNumber", "itemId", "level", "partCode"))
        if (int(drink_to_discount.get("partCode")) in DISCOUNT_ALLOWED_DRINKS):
            discountamt = getProductPrice(
                posid, "50000.%d" % (ALLOWED_DRINKS[0]))  # "1.49"
            message = "Coupon applied!\\The following item has been given a discount:\\\\"
        else:
            discountamt = unitPrice
        posot.applyDiscount(
            discountid, discountamt, linenumber, itemid, level, partcode)
        unitPrice, linenumber, itemid, level, partcode = map(
            side_to_discount.get, ("unitPrice", "lineNumber", "itemId", "level", "partCode"))
        if (int(side_to_discount.get("partCode")) in DISCOUNT_ALLOWED_SIDES):
            discountamt = getProductPrice(
                posid, "50000.%d" % (ALLOWED_SIDES[0]))  # "1.39"
            message = "Coupon applied!\\The following item has been given a discount:\\\\"
        else:
            discountamt = unitPrice
        posot.applyDiscount(
            discountid, discountamt, linenumber, itemid, level, partcode)
        message += "1  " + drink_to_discount.get("productName") + "\\"
        message += "1  " + side_to_discount.get("productName") + "\\"
        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@promotion
def coupon_free_fries_drink5(posid, discountid, extra, *args):
    """
    Free small fries & drink with purchase of a Tuscan Chicken on Ciabatta
    """
    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    check_coupon_validity(posid, model, order, discountid)

    # Lists provided by Scott Weinert
    REQUIRED = (100768,)
    ALLOWED_DRINKS = (100158, 100163, 100168, 100173, 100178, 100188, 100212, 100217, 100222,
                      100227, 100237, 100254, 100259, 100264, 100435, 100474, 100565, 100570, 100597, 100602,)
    DISCOUNT_ALLOWED_DRINKS = (100159, 100160, 100164, 100165, 100169, 100170, 100174, 100175, 100179, 100180, 100213,
                               100214, 100218, 100219, 100223, 100224, 100228, 100229, 100238, 100239, 100255, 100256,
                               100260, 100261, 100265, 100266, 100436, 100475, 100476, 100566, 100567, 100571, 100572,
                               100598, 100599, 100603, 100604, 100597, 100598, 100599, 100698, 100699, 100700, 100703,
                               100704, 100705, 100708, 100709, 100710,)
    ALLOWED_SIDES = (100150,)
    DISCOUNT_ALLOWED_SIDES = (100151, 100152,)
    required_items = []
    allowed_drinks = []
    allowed_sides = []
    for line in order.findall("SaleLine"):
        if int(line.get("level")) != 0:
            continue
        pcode = int(line.get("partCode"))
        qty = float(line.get("qty"))
        if pcode in REQUIRED and qty > 0:
            required_items.append(line)
        if (pcode in ALLOWED_DRINKS or pcode in DISCOUNT_ALLOWED_DRINKS) and qty > 0:
            allowed_drinks.append(line)
        if (pcode in ALLOWED_SIDES or pcode in DISCOUNT_ALLOWED_SIDES) and qty > 0:
            allowed_sides.append(line)
    if (not required_items) or (not allowed_drinks) or (not allowed_sides):
        show_messagebox(
            posid, "This coupon is only valid for a small fries and drink with purchase of a Tuscan Chicken on Ciabatta.\\\\" +
            "Please add the desired items to the order first.", icon="warning")
        return
    drink_to_discount = allowed_drinks[0]
    side_to_discount = allowed_sides[0]
    # Always give the discount in the highest-value item
    for item in allowed_drinks:
        if item in ALLOWED_DRINKS:
            drink_to_discount = item
    for item in allowed_sides:
        if item in ALLOWED_SIDES:
            side_to_discount = item
    try:
        posot = get_posot(model)
        assert_order_discounts(posid, model)
        if float(drink_to_discount.get("qty")) > 1:
            # We need to split the line first
            posot.splitOrderLine(posid, drink_to_discount.get("lineNumber"), 1)
        if float(side_to_discount.get("qty")) > 1:
            # We need to split the line first
            posot.splitOrderLine(posid, side_to_discount.get("lineNumber"), 1)
        # Apply the discount
        message = "Coupon applied!\\The following item has been given for free:\\\\"
        unitPrice, linenumber, itemid, level, partcode = map(
            drink_to_discount.get, ("unitPrice", "lineNumber", "itemId", "level", "partCode"))
        if (int(drink_to_discount.get("partCode")) in DISCOUNT_ALLOWED_DRINKS):
            discountamt = getProductPrice(
                posid, "50000.%d" % (ALLOWED_DRINKS[0]))  # "1.49"
            message = "Coupon applied!\\The following item has been given a discount:\\\\"
        else:
            discountamt = unitPrice
        posot.applyDiscount(
            discountid, discountamt, linenumber, itemid, level, partcode)
        unitPrice, linenumber, itemid, level, partcode = map(
            side_to_discount.get, ("unitPrice", "lineNumber", "itemId", "level", "partCode"))
        if (int(side_to_discount.get("partCode")) in DISCOUNT_ALLOWED_SIDES):
            discountamt = getProductPrice(
                posid, "50000.%d" % (ALLOWED_SIDES[0]))  # "1.39"
            message = "Coupon applied!\\The following item has been given a discount:\\\\"
        else:
            discountamt = unitPrice
        posot.applyDiscount(
            discountid, discountamt, linenumber, itemid, level, partcode)
        message += "1  " + drink_to_discount.get("productName") + "\\"
        message += "1  " + side_to_discount.get("productName") + "\\"
        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@promotion
def coupon_2_off_salad(posid, discountid, extra, *args):
    """
    $2.00 Off any Large Entrée Salad (Full Size)
    """
    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    check_coupon_validity(posid, model, order, discountid)

    ALLOWED = (100514, 100515, 100516, 100517, 100559, 100560, 100754, 100756,
               100758, 100760, 100762, 100764, 100766)  # List provided by Scott Weinert
    lines_allowed = [line for line in order.findall("SaleLine") if int(
        line.get("level")) == 0 and int(line.get("partCode")) in ALLOWED]
    if not lines_allowed:
        show_messagebox(
            posid, "This coupon is only valid for a Large Entrée Salad (Full Size).\\\\" +
            "Please add the desired item to the order first.", icon="warning")
        return
    item_to_discount = lines_allowed[0]
    try:
        posot = get_posot(model)
        assert_order_discounts(posid, model)
        if float(item_to_discount.get("qty")) > 1:
            # We need to split the line first
            posot.splitOrderLine(posid, item_to_discount.get("lineNumber"), 1)
        # Apply the discount
        discountamt = "2.00"
        linenumber, itemid, level, partcode = map(
            item_to_discount.get, ("lineNumber", "itemId", "level", "partCode"))
        posot.applyDiscount(
            discountid, discountamt, linenumber, itemid, level, partcode)
        message = "Coupon applied!\\The following item has been given a $2.00 Off:\\\\"
        message += "1  " + item_to_discount.get("productName") + "\\"
        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@promotion
def coupon_1_off_combomeal(posid, discountid, extra, *args):
    """
    $1.00 Off any combo meal
    """
    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    check_coupon_validity(posid, model, order, discountid)

    ALLOWED = (
        100000, 100001, 100002, 100003, 100004, 100005, 100006, 100007, 100008, 100009, 100010, 100011, 100012,
        100013, 100014, 100015, 100016, 100017, 100018, 100019, 100020, 100021, 100022, 100023, 100024, 100025,
        100026, 100027, 100028, 100029, 100030, 100031, 100032, 100033, 100034, 100035, 100038, 100039, 100040,
        100053, 100054, 100055, 100059, 100060, 100061, 100062, 100063, 100064, 100065, 100066, 100067, 100071,
        100072, 100073, 100115, 100116, 100117, 100349, 100350, 100455, 100458, 100459, 100461, 100462, 100463,
        100465, 100466, 100467, 100469, 100470, 100471, 100482, 100483, 100484, 100486, 100487, 100488, 100490,
        100491, 100492, 100495, 100496, 100497, 100503, 100504, 100505, 100511, 100512, 100513, 100534, 100535,
        100536, 100538, 100539, 100540, 100542, 100543, 100544, 100546, 100547, 100548, 100574, 100575, 100576,
        100580, 100606, 100607, 100608, 100621, 100623, 100624, 100625, 100627, 100628, 100629, 100631, 100632,
        100633, 100634, 100636, 100637, 100638, 100639, 100640, 100641, 100642, 100643, 100644, 100646, 100647,
        100648, 100651, 100657, 100658, 100659, 100661, 100662, 100663, 100665, 100666, 100667, 100669, 100670,
        100671, 100673, 100674, 100675, 100677, 100678, 100679, 100681, 100682, 100683, 100685, 100686, 100687,
    )  # List provided by Scott Weinert
    lines_allowed = [line for line in order.findall("SaleLine") if int(
        line.get("level")) == 0 and int(line.get("partCode")) in ALLOWED]
    if not lines_allowed:
        show_messagebox(
            posid, "This coupon is only valid for a Combo Meal.\\\\Please add the desired item to the order first.", icon="warning")
        return
    item_to_discount = lines_allowed[0]
    try:
        posot = get_posot(model)
        assert_order_discounts(posid, model)
        if float(item_to_discount.get("qty")) > 1:
            # We need to split the line first
            posot.splitOrderLine(posid, item_to_discount.get("lineNumber"), 1)
        # Apply the discount
        discountamt = "1.00"
        linenumber, itemid, level, partcode = map(
            item_to_discount.get, ("lineNumber", "itemId", "level", "partCode"))
        posot.applyDiscount(
            discountid, discountamt, linenumber, itemid, level, partcode)
        message = "Coupon applied!\\The following item has been given a $1.00 Off:\\\\"
        message += "1  " + item_to_discount.get("productName") + "\\"
        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@promotion
def coupon_2singles_2smfries(posid, discountid, extra, *args):
    """
    Two Dave's Hot N' Juicy Single Cheeseburgers & Two Small Fries for $7.99
    """
    # Initializations and first validations
    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    check_coupon_validity(posid, model, order, discountid)
    posot = get_posot(model)
    # Promotion configuration
    REQUIRED = {"100080": {"requires": 2.0}, "100150": {"requires": 2.0}}
    PROMOPRICE = "7.99"
    try:
        # Search for the requirements
        for line in order.findall("SaleLine"):
            if int(line.get("level")) != 0:
                continue
            if line.get("partCode") in REQUIRED.keys():
                qty = float(line.get("qty", "0"))
                if qty > 0 and REQUIRED[line.get("partCode")]["requires"] > 0:
                    if "lines" not in REQUIRED[line.get("partCode")]:
                        REQUIRED[line.get("partCode")]["lines"] = []
                    if (REQUIRED[line.get("partCode")]["requires"] - qty) < 0:
                        posot.splitOrderLine(
                            posid, line.get("lineNumber"), int(REQUIRED[line.get("partCode")]["requires"]))
                        line.set(
                            "qty", str(int(REQUIRED[line.get("partCode")]["requires"])))
                        REQUIRED[line.get("partCode")]["requires"] = 0
                    else:
                        REQUIRED[line.get("partCode")]["requires"] -= qty
                    REQUIRED[line.get("partCode")]["lines"].append(line)
        # Validate the promotion and calculate the orinal total amount
        totamt = D("0.00")
        for r in REQUIRED.values():
            if r["requires"] > 0:
                show_messagebox(
                    posid, "This coupon is only valid for two cheeseburgers and two small fries.\\\\" +
                    "Please add the desired item to the order first.", icon="warning")
                return
            for l in r["lines"]:
                totamt += (D(l.get("unitPrice", "0.00")) * D(l.get("qty")))
        # Check if the discount makes sense
        if totamt < D(PROMOPRICE):
            show_messagebox(
                posid, "The promotional price is greater than the selected items total amount.", icon="warning")
            return
        # Calculate the discount amount
        discamt = totamt - D(PROMOPRICE)
        # Apply the discount on total
        posot.applyDiscount(discountid, str(discamt))
        message = "Coupon applied!\\The discount amount was $%s." % (
            str(discamt))
        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@promotion
def coupon_2chsand_2smfries(posid, discountid, extra, *args):
    """
    Two Large Chicken Sandwiches & Two Small Fries for $7.99
        - Spicy, Homemade or Grilled Chicken Fillet
    """
    # Initializations and first validations
    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    check_coupon_validity(posid, model, order, discountid)
    posot = get_posot(model)
    # Promotion configuration
    REQUIRED = {"100120|100121|100122": {
        "requires": 2.0}, "100150": {"requires": 2.0}}
    PROMOPRICE = "7.99"
    try:
        # Search for the requirements
        for line in order.findall("SaleLine"):
            if int(line.get("level")) != 0:
                continue
            partCode = line.get("partCode")
            for k in REQUIRED.keys():
                if partCode in k.split('|'):
                    qty = float(line.get("qty", "0"))
                    if qty > 0 and REQUIRED[k]["requires"] > 0:
                        if "lines" not in REQUIRED[k]:
                            REQUIRED[k]["lines"] = []
                        if (REQUIRED[k]["requires"] - qty) < 0:
                            posot.splitOrderLine(
                                posid, line.get("lineNumber"), int(REQUIRED[k]["requires"]))
                            line.set("qty", str(int(REQUIRED[k]["requires"])))
                            REQUIRED[k]["requires"] = 0
                        else:
                            REQUIRED[k]["requires"] -= qty
                        REQUIRED[k]["lines"].append(line)
                    break
        # Validate the promotion and calculate the orinal total amount
        totamt = D("0.00")
        for r in REQUIRED.values():
            if r["requires"] > 0:
                show_messagebox(
                    posid, "This coupon is only valid for two large chicken sandwiches and two small fries.\\\\Please add the desired item to the order first.", icon="warning")
                return
            for l in r["lines"]:
                totamt += (D(l.get("unitPrice", "0.00")) * D(l.get("qty")))
        # Check if the discount makes sense
        if totamt < D(PROMOPRICE):
            show_messagebox(
                posid, "The promotional price is greater than the selected items total amount.", icon="warning")
            return
        # Calculate the discount amount
        discamt = totamt - D(PROMOPRICE)
        # Apply the discount on total
        posot.applyDiscount(discountid, str(discamt))
        message = "Coupon applied!\\The discount amount was $%s." % (
            str(discamt))
        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@promotion
def coupon_moonlight_deal(posid, discountid, extra, *args):
    """
    $5 Moonlight Meal Deal consists of a Double Stack, Chili Cheese Fry & Large Drink all for only $5.
    When a customer orders this, simply ring in the individual items, then use the “$5 Moon Meal”
    coupon key to adjust their price back to $5. If a consumer wants a large fry instead of
    chili cheese fries, we can accommodate that order with the “$5 Moon Lg Fry” coupon key that
    will adjust their order back to $5.
    """
    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    check_coupon_validity(posid, model, order, discountid)
    t = time.localtime()
    t = "%02d%02d" % (t.tm_hour, t.tm_min)
    if t > "0300" and t < "2200":
        show_messagebox(
            posid, "This coupon is only valid between 10:00pm and 03:00am.", icon="warning")
        return

    # Lists provided by Scott Weinert
    REQUIRED_AND = (100096, 100160,)
    REQUIRED_OR = (100652, 100152,)
    required_items = []
    required_or = None
    for line in order.findall("SaleLine"):
        if int(line.get("level")) != 0:
            continue
        pcode = int(line.get("partCode"))
        qty = float(line.get("qty"))
        if pcode in REQUIRED_AND and qty > 0 and pcode not in [int(l.get("partCode")) for l in required_items]:
            required_items.append(line)
        elif pcode in REQUIRED_OR:
            if required_or is None or (D(required_or.get("unitPrice")) < D(line.get("unitPrice"))):
                required_or = line
    if not required_items or required_or is None or (len(required_items) != len(REQUIRED_AND)):
        show_messagebox(
            posid, "This coupon is only valid for a Double w/ Lg Drink and Chilli Cheese Fries or Lg Fry.\\\\" +
            "Please add the desired items to the order first.", icon="warning")
        return
    try:
        posot = get_posot(model)
        # Calculate the discount amount
        totamt = D("0.00")
        required_items.append(required_or)
        for l in required_items:
            totamt += D(l.get("unitPrice", "0.00"))
        discamt = totamt - D("5.00")
        # Apply the discount on total
        posot.applyDiscount(discountid, str(discamt))
        message = "Coupon applied!\\The discount amount was $%s." % (
            str(discamt))
        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@promotion
def coupon_guac_it_up(posid, discountid, extra, *args):
    """
    "Guac it Up!" is our new underground menu offering this year. Consumers will utilize social media
    outlets like Facebook and Twitter to spread the following message: “Hey check this out, Wendy’s
    has a new secret underground menu offering! All you have to do is go there after 10pm, order any
    sandwich, and say “I want to Guac It Up!” and they will add guacamole to your sandwich for free!”.
    Ring in their order as you normally would including hitting “Add Guac” on the condiment menu and
    then use the “Guac It Up!” key to give them their free guacamole.
    """
    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    check_coupon_validity(posid, model, order, discountid)
    t = time.localtime()
    t = "%02d%02d" % (t.tm_hour, t.tm_min)
    if t > "0300" and t < "2200":
        show_messagebox(
            posid, "This coupon is only valid between 10:00pm and 03:00am.", icon="warning")
        return

    # Searchs for the guac ingredient on all lines and levels
    item_to_discount = None
    for line in order.findall("SaleLine"):
        pcode = int(line.get("partCode"))
        qty = float(line.get("qty"))
        if pcode != 1241 or qty < 1.0:
            continue
        item_to_discount = line
        break
    if item_to_discount is None:
        show_messagebox(
            posid, "This coupon is only valid for any sandwich with Guacamole ingredient.\\\\" +
            "Please add the desired items to the order first.", icon="warning")
        return
    # Apply the discount
    try:
        posot = get_posot(model)
        # Calculate the discount amount
        discountamt, linenumber, itemid, level, partcode = map(
            item_to_discount.get, ("addedUnitPrice", "lineNumber", "itemId", "level", "partCode"))
        # Apply the discount on total
        posot.applyDiscount(
            discountid, discountamt, linenumber, itemid, level, partcode)
        message = "Coupon applied!"
        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


# -----------------------------------------------------------------------------------------------------------------------------
# Old coupons: maintained for reference only
# -----------------------------------------------------------------------------------------------------------------------------


@promotion
def coupon_free_s_beverage(posid, discountid, extra, *args):
    """
    Free Small 20 oz. Signature Beverage (All Natural Lemonade, Wild Berry Iced Tea, or Wild Berry Lemonade)
    with purchase of any Large sandwich
    """
    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    check_coupon_validity(posid, model, order, discountid)

    # Lists provided by Scott Weinert
    REQUIRED = (100080, 100082, 100084, 100086, 100106, 100118, 100120, 100121,
                100122, 100460, 100464, 100468, 100485, 100489, 100537, 100626, 100630, 100645,)
    ALLOWED = (100565, 100570, 100597, 100602,)
    DISCOUNT_ALLOWED = (
        100566, 100567, 100571, 100572, 100598, 100599, 100603, 100604,)
    required_items = []
    allowed_items = []
    for line in order.findall("SaleLine"):
        if int(line.get("level")) != 0:
            continue
        pcode = int(line.get("partCode"))
        if pcode in REQUIRED:
            required_items.append(line)
        if pcode in ALLOWED or pcode in DISCOUNT_ALLOWED:
            allowed_items.append(line)
    if (not allowed_items) or (not required_items):
        show_messagebox(
            posid, "This coupon is only valid for a Small 20 oz. Signature Beverage " +
            "(All Natural Lemonade, Wild Berry Iced Tea, or Wild Berry Lemonade) with purchase of any Large Sandwich.\\\\" +
            "Please add the desired items to the order first.", icon="warning")
        return
    item_to_discount = allowed_items[0]
    # Always give the discount in the highest-value item
    for item in allowed_items:
        if (D(item.get("unitPrice")) > D(item_to_discount.get("unitPrice"))):
            item_to_discount = item
    try:
        posot = get_posot(model)
        assert_order_discounts(posid, model)
        if float(item_to_discount.get("qty")) > 1:
            # We need to split the line first
            posot.splitOrderLine(posid, item_to_discount.get("lineNumber"), 1)
        # Apply the discount
        discountamt, linenumber, itemid, level, partcode = map(
            item_to_discount.get, ("unitPrice", "lineNumber", "itemId", "level", "partCode"))
        message = "Coupon applied!\\The following item has been given for free:\\\\"
        if (int(item_to_discount.get("partCode")) in DISCOUNT_ALLOWED):
            # "0.79" if price_list.endswith("HH") else "1.79"
            discountamt = getProductPrice(posid, "50000.%d" % (ALLOWED[0]))
            message = "Coupon applied!\\The following item has been given a discount:\\\\"
        posot.applyDiscount(
            discountid, discountamt, linenumber, itemid, level, partcode)
        message += "1  " + item_to_discount.get("productName") + "\\"
        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


def generic_coupon_bogo(posid, discountid, extra, BOGO_CODES, description, *args):
    """
    Buy one, get one promotion script.
    This script applies to:

    1. (Buy One, Get One – BOGO) Free Dave’s Hot ‘N Juicy Single Cheeseburger with the
       purchase of a Dave’s Hot ‘N Juicy Single Cheeseburger
    2. (Buy One, Get One – BOGO) Free Large Chicken Sandwich (Spicy, Homestyle, or
       Grilled) with the purchase of a Large Chicken Sandwich of free of equal or greater value
    @param BOGO_CODES: the list of allowed BOGO product codes (list of int)
    @param description: description of the BOGO item
    """
    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    check_coupon_validity(posid, model, order, discountid)

    ALLOWED = BOGO_CODES
    allowed_items = []
    for line in order.findall("SaleLine"):
        if int(line.get("level")) != 0:
            continue
        pcode = int(line.get("partCode"))
        if pcode in ALLOWED:
            allowed_items.append(line)
    total_qty = sum([float(line.get("qty")) for line in allowed_items])
    if total_qty < 2:
        show_messagebox(
            posid, "This coupon is only valid for %s with the purchase of %s.\\\\" +
            "Please add the desired item to the order first." % (description, description),
            icon="warning")
        return
    item_to_discount = allowed_items[0]
    try:
        posot = get_posot(model)
        assert_order_discounts(posid, model)
        if float(item_to_discount.get("qty")) > 1:
            # We need to split the line first
            posot.splitOrderLine(posid, item_to_discount.get("lineNumber"), 1)
        # Apply the discount
        discountamt, linenumber, itemid, level, partcode = map(
            item_to_discount.get, ("unitPrice", "lineNumber", "itemId", "level", "partCode"))
        posot.applyDiscount(
            discountid, discountamt, linenumber, itemid, level, partcode)
        message = "Coupon applied!\\The following item has been given for free:\\\\"
        message += "1  " + item_to_discount.get("productName") + "\\"
        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@promotion
def coupon_bogo_cheeseburger(posid, discountid, extra, *args):
    """
    (Buy One, Get One - BOGO) Free Dave's Hot 'N Juicy Single Cheeseburger with the
    purchase of a Dave's Hot 'N Juicy Single Cheeseburger
    """
    BOGO_CODES = (100080,)  # List provided by Scott Weinert
    description = "a Single Cheeseburger"
    generic_coupon_bogo(
        posid, discountid, extra, BOGO_CODES, description, *args)


@promotion
def coupon_bogo_tuscan_ch_ciabatta(posid, discountid, extra, *args):
    """
    (Buy One, Get One - BOGO) Free Tuscan Chicken on Ciabatta with the
    purchase of a Tuscan Chicken on Ciabatta
    """
    BOGO_CODES = (100768,)  # List provided by Scott Weinert
    description = "a Single Cheeseburger"
    generic_coupon_bogo(
        posid, discountid, extra, BOGO_CODES, description, *args)


@promotion
def coupon_bogo_large_chicken(posid, discountid, extra, *args):
    """
    (Buy One, Get One - BOGO) Free Large Chicken Sandwich (Spicy, Homestyle, or Grilled)
    with the purchase of a Large Chicken Sandwich of free of equal or greater value
    """
    BOGO_CODES = (100120, 100121, 100122,)  # List provided by Scott Weinert
    description = "a Large Chicken Sandwich (Spicy, Homestyle, or Grilled)"
    generic_coupon_bogo(
        posid, discountid, extra, BOGO_CODES, description, *args)


@promotion
def coupon_free_single_cheeseburger(posid, discountid, extra, *args):
    """
    Free Dave’s Hot 'N Juicy Single Cheeseburger with purchase of a small, medium or large
    fries & drink (20 oz.).

    If a customer would prefer to purchase a Signature Side vs. a Fry, that is acceptable.
    """
    model = extra.get("model") or get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    order = get_current_order(model)
    check_coupon_validity(posid, model, order, discountid)

    # Lists provided by Scott Weinert
    REQUIRED_SIDE = (100150, 100151, 100152, 100649, 100650, 100652,)
    REQUIRED_DRINK = (100158, 100159, 100160, 100163, 100164, 100165, 100168, 100169, 100170, 100173, 100174, 100175,
                      100178, 100179, 100180, 100188, 100190, 100191, 100192, 100198, 100199, 100212, 100213, 100214,
                      100217, 100218, 100219, 100222, 100223, 100224, 100227, 100228, 100229, 100251, 100254, 100255,
                      100256, 100259, 100260, 100261, 100264, 100265, 100266, 100565, 100566, 100567, 100570, 100571,
                      100572, 100597, 100598, 100599, 100602, 100603, 100604, 100597, 100598, 100599, 100698, 100699,
                      100700, 100703, 100704, 100705, 100708, 100709, 100710,)
    ALLOWED = (100080,)
    required_side_items = []
    required_drink_items = []
    allowed_items = []
    for line in order.findall("SaleLine"):
        if int(line.get("level")) != 0:
            continue
        pcode = int(line.get("partCode"))
        if pcode in REQUIRED_SIDE:
            required_side_items.append(line)
        if pcode in REQUIRED_DRINK:
            required_drink_items.append(line)
        if pcode in ALLOWED:
            allowed_items.append(line)
    if (not allowed_items) or (not required_side_items) or (not required_drink_items):
        show_messagebox(
            posid, "This coupon is only valid for a Single Cheeseburger with purchase of\\" +
            "fries & drink (20 oz.)\\A Signature Side vs. a Fry is also accepted.\\\\" +
            "Please add the desired items to the order first.", icon="warning")
        return
    item_to_discount = allowed_items[0]
    # Always give the discount in the highest-value item
    for item in allowed_items:
        if (D(item.get("unitPrice")) > D(item_to_discount.get("unitPrice"))):
            item_to_discount = item
    try:
        posot = get_posot(model)
        assert_order_discounts(posid, model)
        if float(item_to_discount.get("qty")) > 1:
            # We need to split the line first
            posot.splitOrderLine(posid, item_to_discount.get("lineNumber"), 1)
        # Apply the discount
        discountamt, linenumber, itemid, level, partcode = map(
            item_to_discount.get, ("unitPrice", "lineNumber", "itemId", "level", "partCode"))
        posot.applyDiscount(
            discountid, discountamt, linenumber, itemid, level, partcode)
        message = "Coupon applied!\\The following item has been given for free:\\\\"
        message += "1  " + item_to_discount.get("productName") + "\\"
        show_messagebox(posid, message, icon="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@promotion
def surcharge(posid, discountid, extra, amount='0.00', rate='0.00'):
    model = get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    try:
        posot = get_posot(model)

        order_xml = etree.XML(posot.orderPicture(posid))
        total_amount = float(order_xml.get("totalGross")) - float(order_xml.get("taxTotal"))
        if rate:
            amount = float(rate) * float(total_amount) / 100

        for sale_line in order_xml.findall("SaleLine"):
            if sale_line.get("partCode") == str(discountid) and sale_line.get("qty") != "0":
                posot.priceOverwrite(int(posid), unitprice=float(amount), linenumber=sale_line.get("lineNumber"))
                return
        posot.doSale(int(posid), itemid="50000.%s" % discountid, pricelist="EI", qtty=1, verifyOption=False, aftertotal="1")
        posot.priceOverwrite(int(posid), unitprice=float(amount))

        posot.doTotal(posid)
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (
            e.getErrorCode(), e.getErrorDescr()), msgtype="critical")
