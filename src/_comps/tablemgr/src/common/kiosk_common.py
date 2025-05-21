# -*- coding: utf-8 -*-
try:
    from lxml import etree
except:
    import xml.etree.ElementTree as etree

import datetime
import re
import time

import msgbus
import persistence
import json
import posot


def read_swconfig(key, mbcontext):
    """gets a store wide configuration"""
    rmsg = mbcontext.MB_EasySendMessage(
        "StoreWideConfig", token=msgbus.TK_STORECFG_GET,
        format=msgbus.FM_PARAM, data=key
    )

    if rmsg.token == msgbus.TK_SYS_NAK:
        raise Exception("Unable to get Store Wide Configuration key {%s}" % (key, ))

    return str(rmsg.data)


class KioskSession(object):

    def __init__(self, mwapp_component):
        self.logger = mwapp_component.logger
        self.mbcontext = mwapp_component.mbcontext
        self.driver = persistence.Driver()

    def get_session(self, access_token):
        query = "SELECT id, udid, posid, access_token, offline_session, fulfillment_method,\
                 created_on, user_details, identify_details\
                 FROM KioskSession WHERE access_token = '{0}'".format(access_token)

        conn = self.driver.open(self.mbcontext)
        cursor = conn.select(query)
        if cursor.rows() > 0:
            user_details = cursor.get_row(0).get_entry(7)
            if user_details:
                user_details = json.loads(user_details)
            else:
                user_details = {}

            identify_details = cursor.get_row(0).get_entry(8)
            if identify_details:
                identify_details = json.loads(identify_details)
            else:
                identify_details = {}

            session = {
                'id': int(cursor.get_row(0).get_entry(0)),
                'udid': cursor.get_row(0).get_entry(1),
                'pos_id': int(cursor.get_row(0).get_entry(2)),
                'access_token': cursor.get_row(0).get_entry(3),
                'offline_session': cursor.get_row(0).get_entry(4),
                'fulfillment_method': cursor.get_row(0).get_entry(5),
                'created_on': cursor.get_row(0).get_entry(6),
                'user_details': user_details,
                'identify_details': identify_details,
            }
            conn.close()

            return session
        else:
            self.logger.error("No Session ID found for access token {0}.".format(access_token))
            conn.close()

    def create(self, udid, access_token=None, user_details='', identify_details=''):
        offline_session = 0
        self.logger.info('Starting creating session')
        created_on = int(time.time())
        self.access_token = access_token

        user_details = user_details.replace("'", "''")
        identify_details = identify_details.replace("'", "''")

        if not self.access_token:
            offline_session = 1
            self.access_token = "{0}-{1}".format(udid, created_on)
            self.logger.info('Creating offline session.')

        try:
            cafe_id = read_swconfig('Store/Id', self.mbcontext)
            posid_regex = '{cafe_id}(.*\d)'.format(cafe_id=cafe_id)

            posid_match = re.search(posid_regex, udid)
            if posid_match:
                pos_id = int(posid_match.group(1))
            else:
                self.logger.error('Unable to find POS ID for device {0}'.format(udid))
                pos_id = 1  # Default POS ID

            conn = self.driver.open(self.mbcontext)
            query = "INSERT INTO KioskSession (udid, posid, access_token, offline_session, user_details, identify_details) \
                VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}')".format(
                    udid, pos_id, self.access_token, offline_session, user_details, identify_details)
            conn.query(query)
            conn.close()
        except:
            self.logger.exception('Failed to store session in MW:APP')

        return self.access_token

    def set_fulfillment_method(self, access_token, new_fulfillment_method):
        conn = self.driver.open(self.mbcontext)
        query = "UPDATE KioskSession SET fulfillment_method = '{0}' WHERE access_token = '{1}'".format(new_fulfillment_method, access_token)
        conn.query(query)
        conn.close()

    def set_identify_details(self, access_token, identify_details):
        conn = self.driver.open(self.mbcontext)
        query = "UPDATE KioskSession SET identify_details = '{0}' WHERE access_token = '{1}'".format(identify_details, access_token)
        conn.query(query)
        conn.close()


class Purchase(object):

    def __init__(self, mw_component, pos_id, purchase_id=None, purchase_data=None, access_token=None):
        self.mw_component = mw_component
        self.logger = self.mw_component.logger

        self.mbcontext = self.mw_component.mbcontext
        self.cafe_id = read_swconfig('Store/Id', self.mbcontext)

        self.pos_id = int(pos_id)
        self.price_list = "EI"  # 'STD&4&268437503&{cafe_id}'.format(cafe_id=self.cafe_id)
        self.access_token = access_token

        self.driver = persistence.Driver()

        if purchase_id:
            self.mw_line_number, self.mw_purchase_id = self._get_mw_ids(purchase_id)

        self.original_order = None
        if purchase_data:
            if "original_order" in purchase_data.keys():
                self.original_order = purchase_data['original_order']

            self.raw_purchase_data = purchase_data['purchase']
            self._prepare_data(purchase_data['purchase'])

    def _prepare_data(self, raw_purchase_data):
        purchase = json.loads(raw_purchase_data)
        self.purchase_data = purchase
        product_id = self.purchase_data['product']['id']

        self.main_product = product_id
        self.product_options = []

        if self.purchase_data['type'] == 'COMBO':
            for _purchase in self.purchase_data['purchases']:
                self.product_options.append(_purchase['product']['id'])

                if 'selectedPresentationId' in _purchase.keys():
                    self.product_options.append(_purchase['selectedPresentationId'])

                for customization in _purchase['customizations']:
                    if 'variant' in customization.keys():
                        self.product_options.append(customization['variant']['id'])
                    elif 'ingredient' in customization.keys():  # Bagels
                        self.product_options.append(customization['ingredient']['id'])
        else:
            if 'selectedPresentationId' in self.purchase_data.keys():
                self.product_options.append(self.purchase_data['selectedPresentationId'])

            if 'customizations' in self.purchase_data.keys():
                for customization in self.purchase_data['customizations']:
                    if 'variant' in customization.keys():
                        self.product_options.append(customization['variant']['id'])
                    elif 'ingredient' in customization.keys():  # Bagels
                        self.product_options.append(customization['ingredient']['id'])

        if 'sides' in self.purchase_data.keys():
            side_id = self.purchase_data['sides'][0]['id']
            self.product_options.append(side_id)

        options_counter = {}
        for option in self.product_options:
            if option in options_counter.keys():
                options_counter[option] += 1
            else:
                options_counter[option] = 1
        self.product_options = options_counter

        self.mw_main_product = '0.{0}1'.format(self.main_product)
        self.mw_options = {}

        for option, qty in self.product_options.items():
            option_key = '{0}.%{1}1'.format(self.mw_main_product, option)
            self.mw_options[option_key] = qty

        self.product = product_factory(self)

    def _do_sale(self, product):
        pos_ot = posot.OrderTaker(self.pos_id, self.mbcontext)
        pos_ot.businessPeriod = str(datetime.date.today()).replace('-', '')
        sale = pos_ot.doSale(self.pos_id, product, self.price_list, verifyOption=False, aftertotal="0")

        if not sale:
            self.logger.error("Something wrong happend during sale of {0}".format(product))
        else:
            self.logger.debug("Sale of {0} finished.".format(product))
        return sale

    def _get_purchase_id(self, sale):
        sale_tree = etree.fromstring(sale)
        order_id = sale_tree.get('orderId')
        line_number = sale_tree.get('lineNumber')
        purchase_id = "{0}0000{1}".format(order_id, line_number)
        return purchase_id

    def _get_mw_ids(self, purchase_id):
        return purchase_id.rsplit('0000')

    def _store_request_params(self, pos_id, purchase_id, purchase_data, online_purchase_id):
        post_params = json.dumps(purchase_data)

        data = {
            'pos_id': pos_id,
            'post_params': post_params,
            'purchase_id': purchase_id,
            'online_purchase_id': online_purchase_id,
            'original_order': self.original_order,
        }

        # Send to order buffer
        self.mbcontext.MB_EasySendMessage(
            "order_buffer", token=msgbus.TK_BUF_BUFFER_PURCHASE,
            format=msgbus.FM_PARAM, data=json.dumps(data)
        )

    def _do_option(self, option, quantity, line_number):
        query = """SELECT T.ItemCode FROM (
                SELECT (ItemId||'.'||PartCode) ItemCode
                FROM CurrentOrderItem
                WHERE (ItemId||'.'||PartCode)
                LIKE '{0}'
                ORDER BY Level LIMIT 1) T""".format(option)

        conn = self.driver.open(self.mbcontext, dbname=str(self.pos_id))
        cursor = conn.select(query)
        if cursor.rows() > 0:
            option_code = cursor.get_row(0).get_entry(0)
            update = """UPDATE CurrentOrderItem
                SET OrderedQty={0}
                WHERE (ItemId||'.'||PartCode) = '{1}'
                AND LineNumber = {2}""".format(quantity, option_code, line_number)
            cursor = conn.query(update)
        else:
            self.logger.error("Item Code for option {0} not found.".format(option))

        conn.close()
        self.logger.debug("Option {0} finished.".format(option))

    def create_line(self, post_params=None):
        """ purchase.create_line() -> None

            Create an order item in current order

            @param None
            @return: None
        """
        self.logger.debug("Creating a new line in this order.")
        product = None
        if post_params:
            ot = posot.OrderTaker(self.pos_id, self.mbcontext)
            ot.businessPeriod = str(datetime.date.today()).replace('-', '')
            sale = ot.doSale(
                self.pos_id, product, self.price_list,
                verifyOption=False, aftertotal="0")

        if not sale:
            self.logger.error("Something wrong happend during sale of {0}".format(product))
        else:
            self.logger.debug("Sale of {0} finished.".format(product))
        return sale

        sale = self._do_sale(self.mw_main_product)
        self.product.purchase_id = self._get_purchase_id(sale)
        self.mw_purchase_id, self.mw_line_number = self._get_mw_ids(self.product.purchase_id)

        for option, quantity in self.mw_options.items():
            self.logger.info(option)
            self._do_option(option, quantity, self.mw_line_number)

        online_purchase_id = ''
        self._store_request_params(self.pos_id, self.product.purchase_id, self.purchase_data, online_purchase_id)

    def delete_line(self, order_id, line_number):
        """ purchase.delete_line(order_id, line_number) -> None

            Delete an item of the current order

            @param order_id: {int} The id of the current order line that should be deleted
            @param line_number: {int} The line number of the current order that should be deleted
            @return: None
        """
        self.logger.debug("Deleting line {0} of current order.".format(line_number))

        _posot = posot.OrderTaker(self.pos_id, self.mbcontext)
        _posot.voidLine(self.pos_id, line_number)

        update = """UPDATE CurrentOrderItem
                    SET OrderedQty=0, LastOrderedQty=1
                    WHERE LineNumber = {0} AND OrderedQty > 0""".format(line_number)
        conn = self.driver.open(self.mbcontext, dbname=str(self.pos_id))
        conn.query(update)

        delete_line_query = """DELETE FROM PurchaseItems
            WHERE pos_id = '{0}' AND purchase_id = '{1}0000{2}'""".format(
            self.pos_id, order_id, line_number)
        conn.query(delete_line_query)

        delete_discount_query = """DELETE FROM OrderDiscounts
            WHERE purchase_id = '{0}0000{1}'""".format(
            order_id, line_number)
        conn.query(delete_discount_query)

        conn.close()

    def update_line(self, purchase_id, new_purchase_data):
        """ purchase.update_line(purchase_id, purchase_data) -> None

            Update an order item in current order

            @param purchase_id: {str} The full identifier of an order item.
            @param new_purchase_data: {str} Data posted by Kiosk of the new content of the line
            @return: None
        """
        self.logger.debug("Updating item {0}.".format(purchase_id))
        order_id, line_number = purchase_id.rsplit('0000')

        purchase_data = json.loads(new_purchase_data['purchase'])

        main_product_query = "SELECT PartCode FROM CurrentOrderItem WHERE \
            Level = 0 AND OrderId = {0} AND LineNumber = {1}".format(order_id, line_number)

        conn = self.driver.open(self.mbcontext, dbname=str(self.pos_id))
        cursor = conn.select(main_product_query)
        if cursor.rows() > 0:
            main_product_id = cursor.get_row(0).get_entry(0)
            purchase_data['product']['id'] = main_product_id[:-1]
            raw_purchase_data = json.dumps(purchase_data)
        else:
            raw_purchase_data = new_purchase_data['purchase']

        self._prepare_data(raw_purchase_data)
        self.product.purchase_id = purchase_id

        clear_quantities_query = """UPDATE CurrentOrderItem SET OrderedQty = NULL
            WHERE OrderId = {0} AND LineNumber = {1}""".format(order_id, line_number)
        conn.query(clear_quantities_query)

        main_product_query = u"""UPDATE CurrentOrderItem SET OrderedQty = 1
            WHERE OrderId = {0} AND LineNumber = {1} AND (ItemId||'.'||PartCode)
                LIKE '{2}'""".format(order_id, line_number, self.mw_main_product)
        conn.query(main_product_query)

        for option, quantity in self.mw_options.items():
            option_query = u"""UPDATE CurrentOrderItem SET OrderedQty = 1
                WHERE OrderId = {0} AND LineNumber = {1} AND (ItemId||'.'||PartCode)
                    LIKE '{2}'""".format(order_id, line_number, option)
            conn.query(option_query)

        purchase_data.pop("id", None)
        update_query = "UPDATE PurchaseItems SET post_params = '{0}' WHERE purchase_id = '{1}'".format(json.dumps(purchase_data), purchase_id)
        conn.query(update_query)

        conn.close()

    def get_order_price(self):
        conn = self.driver.open(self.mbcontext, dbname=str(self.pos_id))

        user_details = None
        fulfillment_method = 1  # Default fulfillment method
        if self.access_token:
            query = "SELECT fulfillment_method, user_details FROM KioskSession WHERE access_token = '{0}'".format(self.access_token)
            cursor = conn.select(query)
            if cursor.rows() > 0:
                fulfillment_method = cursor.get_row(0).get_entry(0)
                user_details = cursor.get_row(0).get_entry(1)

        response = {
            "cafeId": int(self.cafe_id),
            "kioskId": self.pos_id,
            "selectedFulfillmentMethodId": int(fulfillment_method),
            "createdDateTime": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "fulfillmentDateTime": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # TODO
            "orderPricings": [],
            "id": 0
        }

        if user_details:
            user_details = json.loads(user_details)
            if 'firstName' in user_details.keys():
                response['customerFirstName'] = user_details['firstName']

            if 'lastName' in user_details.keys():
                response['customerLastName'] = user_details['lastName']

            if 'contactInformation' in user_details.keys():
                response['customerEmail'] = user_details['contactInformation']['emailAddress']

        params = (self.pos_id, )
        reqbuf = "\0".join(str(p) for p in params)
        msg = self.mbcontext.MB_EasySendMessage(
            "ORDERMGR%s" % (self.pos_id), msgbus.TK_SLCTRL_OMGR_ORDERPICT,
            msgbus.FM_PARAM, reqbuf
        )

        # if "state=\"VOIDED\"" in msg.data:
        if any(x in msg.data for x in ("state=\"VOIDED\"", "state=\"ABANDON\"")):
            response['status'] = 'NEW'
            return json.dumps(response)

        params = msg.data.split('\0')
        if msg.token == msgbus.TK_SYS_NAK:
            raise posot.OrderTakerException(params[0], params[1])

        price_tree = etree.fromstring(params[2])

        totalAmount = float(price_tree.get("totalAmount", 0.0))
        totalAfterDiscount = float(price_tree.get("totalAfterDiscount", 0.0))
        totalGross = float(price_tree.get("totalGross", 0.0))
        taxTotal = float(price_tree.get("taxTotal", 0.0))

        total_amount = totalAfterDiscount

        codes_query = "SELECT SUM(OrderedQty), PartCode FROM CurrentOrderItem WHERE OrderedQty > 0 GROUP BY PartCode"

        parts = {}
        part_codes = []
        cursor = conn.select(codes_query)
        if cursor.rows() > 0:
            for row in cursor:
                part_multiplier = row.get_entry(0)
                part_code = row.get_entry(1)
                part_codes.append(part_code)
                parts[part_code] = part_multiplier

        codes = '({0})'.format(', '.join(part_codes))
        query = """
            SELECT
                DISTINCT TR.TaxRate, P.DefaultUnitPrice, PTC.ItemId
            FROM
                TaxRule TR
            JOIN
                TaxCategory TC ON TR.TaxCgyId = TC.TaxCgyId
            JOIN
                ProductTaxCategory PTC ON PTC.TaxCgyId = TC.TaxCgyId
            JOIN
                Price P ON P.ProductCode = PTC.ItemId
            WHERE
                P.DefaultUnitPrice > 0
                AND PTC.ItemId IN {0}""".format(codes)

        total_tax_value = 0
        cursor = conn.select(query)
        if cursor.rows() > 0:
            for row in cursor:
                part_code = row.get_entry(2)
                multiplier = int(parts[part_code])
                tax_percent = float(row.get_entry(0))
                unit_price = float(row.get_entry(1)) * multiplier
                tax_value = round(unit_price * tax_percent, 2)
                total_tax_value += tax_value
        else:
            self.logger.error("Prices not found.")

        discount_amount = None
        if self.access_token:
            discount_query = """SELECT discount_id, purchase_id FROM OrderDiscounts WHERE access_token = '{0}'""".format(self.access_token)
            cursor = conn.select(discount_query)
            if cursor.rows() > 0:
                discount_id = cursor.get_row(0).get_entry(0)
                purchase_id = cursor.get_row(0).get_entry(1)

                if purchase_id == '0':
                    base_amount = total_amount
                else:
                    order_id, line_number = purchase_id.rsplit('0000')
                    codes_query = """SELECT SUM(OrderedQty), PartCode
                        FROM CurrentOrderItem WHERE OrderedQty > 0 AND OrderId = '{0}'
                        AND LineNumber = {1} GROUP BY PartCode""".format(order_id, line_number)
                    parts = {}
                    part_codes = []
                    cursor = conn.select(codes_query)
                    if cursor.rows() > 0:
                        for row in cursor:
                            part_multiplier = row.get_entry(0)
                            part_code = row.get_entry(1)
                            part_codes.append(part_code)
                            parts[part_code] = part_multiplier
                    codes = '({0})'.format(', '.join(part_codes))
                    query = """
                        SELECT
                            DISTINCT TR.TaxRate, P.DefaultUnitPrice, PTC.ItemId
                        FROM
                            TaxRule TR
                        JOIN
                            TaxCategory TC ON TR.TaxCgyId = TC.TaxCgyId
                        JOIN
                            ProductTaxCategory PTC ON PTC.TaxCgyId = TC.TaxCgyId
                        JOIN
                            Price P ON P.ProductCode = PTC.ItemId
                        WHERE
                            P.DefaultUnitPrice > 0
                            AND PTC.ItemId IN {0}""".format(codes)
                    cursor = conn.select(query)
                    base_amount = 0
                    if cursor.rows() > 0:
                        for row in cursor:
                            multiplier = int(parts[part_code])
                            unit_price = float(row.get_entry(1)) * multiplier
                            base_amount += unit_price
                    else:
                        base_amount = total_amount

                discount_query = """SELECT DISCOUNTTYPE, SCOPE, PERCENTRATE, DOLLARRATE
                    FROM TBL_DISCOUNTS
                    WHERE DISCOUNTCODE = '{0}'""".format(discount_id)
                cursor = conn.select(discount_query)
                if cursor.rows() > 0:
                    discount_type = cursor.get_row(0).get_entry(0)
                    percent_rate = int(cursor.get_row(0).get_entry(2))
                    dollar_rate = float(cursor.get_row(0).get_entry(3))
                    if discount_type == '1':
                        discount_amount = dollar_rate
                    elif discount_type == '2':
                        discount_amount = base_amount * (percent_rate / 100.0)

        conn.close()

        response['status'] = "IN_PROGRESS"
        response['id'] = int(price_tree.get('orderId', 0))

        orderPricings = []
        fulfillment_methods = [1, 2, ]
        for method in fulfillment_methods:
            if discount_amount:
                tax_value = tax_percent * (total_amount - discount_amount)
                pricing = {
                    "subtotalWithoutDiscount": round(totalAmount, 2),
                    "discount": round(discount_amount, 2),
                    "subtotal": round(totalAfterDiscount, 2),
                    "taxPercentage": int(round(tax_percent, 2) * 100),
                    "taxValue": round(taxTotal, 2),
                    "fulfillmentMethodId": method,
                    "deliveryFee": 0,
                    "total": round(totalGross, 2),
                }
            else:
                pricing = {
                    "fulfillmentMethodId": method,
                    "taxValue": round(taxTotal, 2),
                    "subtotal": round(totalAmount, 2),
                    "total": round(totalGross, 2),
                    "subtotalWithoutDiscount": round(totalAmount, 2),
                    "discount": 0,
                    "deliveryFee": 0
                }
            orderPricings.append(pricing)

        response["orderPricings"] = orderPricings

        return json.dumps(response)

    def set_panera_id(self, panera_id):
        params = (self.pos_id, )
        reqbuf = "\0".join(str(p) for p in params)
        msg = self.mbcontext.MB_EasySendMessage(
            "ORDERMGR%s" % (self.pos_id), msgbus.TK_SLCTRL_OMGR_ORDERPICT,
            msgbus.FM_PARAM, reqbuf
        )
        params = msg.data.split('\0')
        if msg.token == msgbus.TK_SYS_NAK:
            raise posot.OrderTakerException(params[0], params[1])
        order_tree = etree.fromstring(params[2])
        order_id = int(order_tree.get('orderId', 0))

        query = "SELECT panera_id FROM Purchases WHERE purchase_id = '{0}'".format(order_id)

        conn = self.driver.open(self.mbcontext, dbname=str(self.pos_id))
        cursor = conn.select(query)
        if cursor.rows() > 0:
            query = "UPDATE Purchases SET panera_id = '{0}' WHERE purchase_id = '{1}'".format(panera_id, order_id)
        else:
            query = "INSERT INTO Purchases (purchase_id, panera_id) \
                VALUES ('{0}', '{1}')".format(order_id, panera_id)
        conn.query(query)
        conn.close()

    @property
    def panera_id(self):
        params = (self.pos_id, )
        reqbuf = "\0".join(str(p) for p in params)
        msg = self.mbcontext.MB_EasySendMessage(
            "ORDERMGR%s" % (self.pos_id), msgbus.TK_SLCTRL_OMGR_ORDERPICT,
            msgbus.FM_PARAM, reqbuf
        )
        params = msg.data.split('\0')
        if msg.token == msgbus.TK_SYS_NAK:
            raise posot.OrderTakerException(params[0], params[1])
        order_tree = etree.fromstring(params[2])
        purchase_id = int(order_tree.get('orderId', 0))

        query = "SELECT panera_id FROM Purchases \
            WHERE purchase_id = '{0}'".format(purchase_id)

        conn = self.driver.open(self.mbcontext, dbname=str(self.pos_id))
        cursor = conn.select(query)
        if cursor.rows() > 0:
            conn.close()
            return cursor.get_row(0).get_entry(0)
        conn.close()


class Combo(object):

    def __init__(self, purchase):
        self.mw_component = purchase.mw_component
        self.logger = self.mw_component.logger
        self.mbcontext = self.mw_component.mbcontext

        self.pos_id = purchase.pos_id
        self.purchase = purchase

        self.type = purchase.purchase_data['type']
        self.selectedFulfillmentMethod = purchase.purchase_data['selectedFulfillmentMethodId']

        if 'customizations' in purchase.purchase_data.keys():
            self.customizations = purchase.purchase_data['customizations']

        if 'sides' in purchase.purchase_data.keys():
            self.side = purchase.purchase_data['sides'][0]['id']

        self.quantity = 1
        self.purchase_id = None

        self.specialInstructions = purchase.purchase_data['specialInstructions'] if 'specialInstructions' in purchase.purchase_data.keys() else None
        self.preparedFor = purchase.purchase_data['preparedFor'] if 'preparedFor' in purchase.purchase_data.keys() else None

    def response(self):
        response = {
            'type': self.type,
            'selectedFulfillmentMethod': self.selectedFulfillmentMethod,
            'quantity': self.quantity,
            'purchases': [
            ],
            'product': {
                'id': self.purchase.main_product
            },
            'id': int(self.purchase_id)
        }

        if self.specialInstructions:
            response['specialInstructions'] = self.specialInstructions
        if self.preparedFor:
            response['preparedFor'] = self.preparedFor

        return json.dumps(response)


class SimpleProduct(object):

    def __init__(self, purchase):
        self.mw_component = purchase.mw_component
        self.logger = self.mw_component.logger
        self.mbcontext = self.mw_component.mbcontext

        self.pos_id = purchase.pos_id
        self.purchase = purchase
        self.product_id = None

        self.type = purchase.purchase_data['type']
        self.selectedFulfillmentMethod = purchase.purchase_data['selectedFulfillmentMethodId']

    def response(self):
        response = {
            'type': self.type,
            'selectedFulfillmentMethod': self.selectedFulfillmentMethod,
            'product': {
                'id': self.purchase.main_product
            },
            'id': int(self.purchase_id)
        }

        return json.dumps(response)


class CommonProduct(object):

    def __init__(self, purchase):
        self.mw_component = purchase.mw_component
        self.logger = self.mw_component.logger
        self.mbcontext = self.mw_component.mbcontext

        self.pos_id = purchase.pos_id
        self.purchase = purchase

        self.type = purchase.purchase_data['type']
        self.selectedFulfillmentMethod = purchase.purchase_data['selectedFulfillmentMethodId']

        if 'customizations' in purchase.purchase_data.keys():
            self.customizations = purchase.purchase_data['customizations']

        if 'sides' in purchase.purchase_data.keys():
            self.side = purchase.purchase_data['sides'][0]['id']

        self.quantity = 1
        self.purchase_id = None
        self.selectedPresentationId = purchase.purchase_data['selectedPresentationId']

        self.specialInstructions = purchase.purchase_data['specialInstructions'] if 'specialInstructions' in purchase.purchase_data.keys() else None
        self.preparedFor = purchase.purchase_data['preparedFor'] if 'preparedFor' in purchase.purchase_data.keys() else None

    def response(self):
        response = {
            'type': self.type,
            'selectedFulfillmentMethod': self.selectedFulfillmentMethod,
            'selectedPresentationId': self.selectedPresentationId,
            'quantity': self.quantity,
            'id': int(self.purchase_id),
        }

        if self.specialInstructions:
            response['specialInstructions'] = self.specialInstructions
        if self.preparedFor:
            response['preparedFor'] = self.preparedFor

        return json.dumps(response)


def product_factory(purchase):
    if purchase.purchase_data['type'] == 'COMBO':
        return Combo(purchase)
    elif 'selectedPresentationId' in purchase.purchase_data.keys():
        return CommonProduct(purchase)
    else:
        return SimpleProduct(purchase)
