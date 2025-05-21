# -*- coding: utf-8 -*-

import datetime
import json
import time
from threading import Thread
from xml.etree import cElementTree as eTree

import iso8601
import msgbus
import sysactions
from application.customexception import OrderException, PaymentException, FiscalException
from application.model import RemoteOrder, BusTokens
from application.repository import ProductRepository, FiscalRepository
from application.services import DefaultQuantityFixer, logger, PosStateFixer
from application.util import validate_cnpj, validate_cpf
from helper import round_half_away_from_zero
from posot import OrderTakerException


class OrderTakerWrapper(object):
    DatabaseDateTimeFormat = "%Y-%m-%d %H:%M:%S"
    
    def __init__(self,
                 mbcontext,
                 fiscal_repository,
                 product_repository,
                 default_quantity_fixer,
                 pos_state_fixer,
                 delivery_user_id,
                 delivery_password,
                 price_list_id,
                 print_app_coupon,
                 printer_max_retries,
                 printer_retry_time,
                 sell_with_partner_price,
                 apply_default_options):
        # type: (msgbus.MBEasyContext, FiscalRepository, ProductRepository, DefaultQuantityFixer, PosStateFixer, unicode, unicode, unicode, bool, int, int, bool, bool) -> None # noqa
        self.mbcontext = mbcontext
        self.fiscal_repository = fiscal_repository
        self.product_repository = product_repository
        self.default_quantity_fixer = default_quantity_fixer
        self.pos_state_fixer = pos_state_fixer
        self.delivery_user_id = delivery_user_id
        self.delivery_password = delivery_password
        self.price_list_id = price_list_id
        self.print_app_coupon = print_app_coupon
        self.printer_max_retries = printer_max_retries
        self.printer_retry_time = printer_retry_time
        self.sell_with_partner_price = sell_with_partner_price
        self.apply_default_options = apply_default_options
        
        sysactions.mbcontext = mbcontext
    
    def check_business_period(self, pos_id):
        model = sysactions.get_model(pos_id)
        current_date = datetime.datetime.now().date().strftime("%Y%m%d")
        
        order_taker = sysactions.get_posot(model)
        try:
            if sysactions.has_current_order(model):
                self._void_order(order_taker, pos_id)
        
        except OrderTakerException:
            pass
        
        model = sysactions.get_model(pos_id)
        operator = model.find("Operator")
        if operator is not None and operator.get("state") == "LOGGEDIN":
            operator_id = operator.get("id")
            if operator_id != self.delivery_user_id:
                logger.info("Wrong user logged. Logging off user")
                
                logout_msg = self.mbcontext.MB_EasySendMessage("POS%d" % pos_id, msgbus.TK_POS_USERLOGOUT,
                                                               msgbus.FM_PARAM, "%s\0%s" % (pos_id, operator_id),
                                                               timeout=10000000)
                if logout_msg.token == msgbus.TK_SYS_ACK:
                    if logout_msg.data:
                        raise OrderException("Error logging off user: {}".format(logout_msg.data))
                    raise OrderException("Error logging off user")
                operator = None
        
        if model.find("PosState").get("period") != current_date or model.find("PosState").get("state") != "OPENED":
            logger.info("We need to close business day. Wrong business period or state is not opened")
            
            self.pos_state_fixer.fix_business_period(pos_id)
            
            if operator is not None and operator.get("state") == "LOGGEDIN":
                logger.info("Logging out delivery user")
                logout_msg = self.mbcontext.MB_EasySendMessage("POS%d" % pos_id, msgbus.TK_POS_USERLOGOUT,
                                                               msgbus.FM_PARAM, "%s\0%s" % (
                                                                       pos_id, self.delivery_user_id.encode("utf-8")),
                                                               timeout=10000000)
                if logout_msg.token != msgbus.TK_SYS_ACK:
                    if logout_msg.data:
                        raise OrderException("Error logging off user: {}".format(logout_msg.data))
                    raise OrderException("Error logging off user")
                
                operator = None
            
            if model.find("PosState").get("state") == "OPENED" or model.find("PosState").get("state") == "BLOCKED":
                logger.info("Closing business current period")
                business_end_msg = self.mbcontext.MB_EasySendMessage("POS%d" % pos_id, msgbus.TK_POS_BUSINESSEND,
                                                                     msgbus.FM_PARAM, "%s" % pos_id, timeout=10000000)
                if business_end_msg.token != msgbus.TK_SYS_ACK:
                    if business_end_msg.data:
                        raise OrderException("Error closing day: {}".format(business_end_msg.data))
                    raise OrderException("Error closing day")
            
            logger.info("Opening business period")
            business_begin_msg = self.mbcontext.MB_EasySendMessage("POS%d" % pos_id, msgbus.TK_POS_BUSINESSBEGIN,
                                                                   msgbus.FM_PARAM, "%s\0%s" % (pos_id, current_date),
                                                                   timeout=10000000)
            if business_begin_msg.token != msgbus.TK_SYS_ACK:
                if business_begin_msg.data:
                    raise OrderException("Error opening day: {}".format(business_begin_msg.data))
                raise OrderException("Error opening day")
        
        if operator is None or operator.get("state") != "LOGGEDIN":
            logger.info("Authenticate delivery user")
            authenticate_msg = self.mbcontext.MB_EasySendMessage('UserControl', msgbus.TK_USERCTRL_AUTHENTICATE,
                                                                 msgbus.FM_PARAM, '%s\x00%s\x00' %
                                                                 (self.delivery_user_id.encode("utf-8"),
                                                                  self.delivery_password.encode("utf-8")),
                                                                 timeout=10000000)
            if authenticate_msg.token != msgbus.TK_SYS_ACK:
                if authenticate_msg.data:
                    raise OrderException("Error authentication delivery user: {}".format(authenticate_msg.data))
                raise OrderException("Error authentication delivery user")
            
            level, username, long_user_name = authenticate_msg.data.split('\x00')[:3]
            
            if operator is None or (operator.get("state") != "OPENED" and operator.get("state") != "PAUSED"):
                logger.info("Opening delivery user")
                open_user_message = self.mbcontext.MB_EasySendMessage("POS%d" % int(pos_id), msgbus.TK_POS_USEROPEN,
                                                                      msgbus.FM_PARAM, "%s\0%s\0%s\0%s" % (
                                                                              pos_id,
                                                                              self.delivery_user_id.encode("utf-8"),
                                                                              0.0, long_user_name), timeout=10000000)
                if open_user_message.token != msgbus.TK_SYS_ACK:
                    if open_user_message.data:
                        raise OrderException("Error opening user: {}".format(open_user_message.data))
                    raise OrderException("Error opening user")
            
            logger.info("Logging delivery user")
            login_msg = self.mbcontext.MB_EasySendMessage("POS%d" % int(pos_id), msgbus.TK_POS_USERLOGIN,
                                                          msgbus.FM_PARAM, "%s\0%s\0%s" % (
                                                                  pos_id, self.delivery_user_id.encode("utf-8"),
                                                                  long_user_name),
                                                          timeout=10000000)
            if login_msg.token != msgbus.TK_SYS_ACK:
                if login_msg.data:
                    raise OrderException("Error logging in Delivery user: {}".format(login_msg.data))
                raise OrderException("Error logging in Delivery user")
    
    @staticmethod
    def _void_order(order_taker, pos_id):
        order_taker.voidOrder(pos_id)
        time_limit = time.time() + 5.0
        while time.time() < time_limit and sysactions.has_current_order(sysactions.get_model(pos_id)):
            time.sleep(0.1)
    
    def create_order(self, pos_id, remote_order):
        # type: (int, RemoteOrder) -> int
        model = sysactions.get_model(pos_id)
        order_taker = sysactions.get_posot(model)
        try:
            if sysactions.has_current_order(model):
                order_taker.voidOrder(pos_id)
        except OrderTakerException:
            pass
        
        order_sub_type = remote_order.pickup.type if remote_order.pickup.type is not None else ""
        attributes = order_taker.createOrder(posid=pos_id,
                                             pricelist=self.price_list_id.encode("utf-8"),
                                             saletype="DELIVERY",
                                             orderType="SALE",
                                             orderSubType=order_sub_type)
        
        if remote_order.pickup.type == "delivery":
            order_taker.updateOrderProperties(pos_id, saletype="DELIVERY")
        else:
            order_taker.updateOrderProperties(pos_id, saletype="APP")
        
        dict_order_taker = dict()
        
        if remote_order.custom_properties is not None and len(remote_order.custom_properties) > 0:
            for key, value in remote_order.custom_properties.items():
                dict_order_taker.update({key: value.value})
            
            def get_custom(props, prop_dict):
                for prop in props:
                    if prop in prop_dict:
                        return prop_dict.get(prop).value
                    elif prop.upper() in prop_dict:
                        return prop_dict.get(prop.upper()).value
            
            customer_name = get_custom(["customer_name"], remote_order.custom_properties)
            if customer_name:
                filtered_customer_name = self._filter_customer_name(customer_name.encode("utf-8"))
                if filtered_customer_name:
                    dict_order_taker.update({"CUSTOMER_NAME": filtered_customer_name})
            
            document_value = get_custom(["customer_doc", "customer_document"], remote_order.custom_properties)
            if document_value:
                valid = validate_cpf(document_value)
                if not valid:
                    valid = validate_cnpj(document_value)
                
                if valid:
                    dict_order_taker.update({"CUSTOMER_DOC": valid.encode("utf-8")})
            
            crm_data = get_custom(["crm"], remote_order.custom_properties)
            if crm_data:
                crm_data = json.loads(crm_data)
                dict_order_taker.update({
                        "CRM_COUPON_SENT": "true",
                        "CRM_COUPON_DATA": json.dumps([{
                                "coupon": {
                                        "partCode": coupon['part_code'],
                                        "externalId": coupon['external_id']
                                },
                                "reference": coupon['reference'],
                                "customerId": coupon['customer_id']
                        } for coupon in crm_data])
                })
        
        dict_order_taker.update({"CREATED_AT": remote_order.created_at.strftime(self.DatabaseDateTimeFormat)})
        if remote_order.pickup.time is not None:
            dict_order_taker.update({"PICKUP_TIME": remote_order.pickup.time.strftime(self.DatabaseDateTimeFormat)})
        
        dict_order_taker.update({"PICKUP_TYPE": remote_order.pickup.type.encode("utf-8")})
        dict_order_taker.update({"REMOTE_ORDER_ID": remote_order.id.encode("utf-8")})
        dict_order_taker.update({"REMOTE_ORDER_CODE": remote_order.code.encode("utf-8")})
        dict_order_taker.update({"PARTNER": remote_order.partner.encode("utf-8")})
        dict_order_taker.update({"SHORT_REFERENCE": remote_order.short_reference.encode("utf-8")})
        dict_order_taker.update({"TENDER_TYPE": remote_order.tenders[0].type})
        
        if remote_order.pickup.address is not None:
            address_object = remote_order.pickup.address
            
            def _is_valid(text_field):
                return True if (text_field is not None and len(text_field) > 0) else False
            
            if hasattr(address_object, 'formattedAddress') and _is_valid(address_object.formattedAddress):
                dict_order_taker.update({"FORMATTED_ADDRESS": address_object.formattedAddress.encode("utf-8")})
            if hasattr(address_object, 'state') and _is_valid(address_object.state):
                dict_order_taker.update({"STATE": address_object.state.encode("utf-8")})
            if hasattr(address_object, 'city') and _is_valid(address_object.city):
                dict_order_taker.update({"CITY": address_object.city.encode("utf-8")})
            if hasattr(address_object, 'neighborhood') and _is_valid(address_object.neighborhood):
                dict_order_taker.update({"NEIGHBORHOOD": address_object.neighborhood.encode("utf-8")})
            if hasattr(address_object, 'streetName') and _is_valid(address_object.streetName):
                dict_order_taker.update({"STREET_NAME": address_object.streetName.encode("utf-8")})
            if hasattr(address_object, 'streetNumber') and _is_valid(address_object.streetNumber):
                dict_order_taker.update({"STREET_NUMBER": address_object.streetNumber.encode("utf-8")})
            if hasattr(address_object, 'postalCode') and _is_valid(address_object.postalCode):
                dict_order_taker.update({"POSTAL_CODE": address_object.postalCode.encode("utf-8")})
            if hasattr(address_object, 'complement') and _is_valid(address_object.complement):
                dict_order_taker.update({"COMPLEMENT": address_object.complement.encode("utf-8")})
            if hasattr(address_object, 'reference') and _is_valid(address_object.reference):
                dict_order_taker.update({"REFERENCE": address_object.reference.encode("utf-8")})
        
        self.fill_additional_info(pos_id, order_taker, dict_order_taker)
        
        order_taker.setOrderCustomProperties(dict_order_taker)
        
        return int(attributes["orderId"])
    
    def essential_create_order(self, pos_id, remote_order):
        # type: (int, RemoteOrder) -> int
        model = sysactions.get_model(pos_id)
        order_taker = sysactions.get_posot(model)
        try:
            if sysactions.has_current_order(model):
                order_taker.voidOrder(pos_id)
        except OrderTakerException:
            pass
        
        attributes = order_taker.createOrder(posid=pos_id,
                                             pricelist=self.price_list_id.encode("utf-8"),
                                             saletype="DELIVERY",
                                             orderType="SALE",
                                             orderSubType="delivery")
        order_taker.updateOrderProperties(pos_id, saletype="DELIVERY")
        
        dict_order_taker = dict()
        
        if remote_order.custom_properties is not None and len(remote_order.custom_properties) > 0:
            for key, value in remote_order.custom_properties.items():
                dict_order_taker.update({key: value.value})
            if "customer_name" in remote_order.custom_properties:
                customer_name = remote_order.custom_properties["customer_name"].value.encode("utf-8")
                filtered_customer_name = self._filter_customer_name(customer_name)
                if filtered_customer_name:
                    dict_order_taker.update({"CUSTOMER_NAME": filtered_customer_name})
        dict_order_taker.update({"CREATED_AT": remote_order.created_at.strftime(self.DatabaseDateTimeFormat)})
        if remote_order.pickup.time is not None:
            dict_order_taker.update({"PICKUP_TIME": remote_order.pickup.time.strftime(self.DatabaseDateTimeFormat)})
        dict_order_taker.update({'PICKUP_TYPE': 'delivery'})
        dict_order_taker.update({"REMOTE_ORDER_ID": remote_order.id.encode("utf-8")})
        dict_order_taker.update({"REMOTE_ORDER_CODE": remote_order.code.encode("utf-8")})
        dict_order_taker.update({"PARTNER": remote_order.partner.encode("utf-8")})
        dict_order_taker.update({"SHORT_REFERENCE": remote_order.short_reference.encode("utf-8")})
        order_taker.setOrderCustomProperties(dict_order_taker)
        
        return int(attributes["orderId"])
    
    @staticmethod
    def fill_additional_info(pos_id, order_taker, dict_order_taker):
        customer_document = dict_order_taker["CUSTOMER_DOC"] if "CUSTOMER_DOC" in dict_order_taker else ""
        customer_name = dict_order_taker["CUSTOMER_NAME"] if "CUSTOMER_NAME" in dict_order_taker else ""
        customer_address = dict_order_taker["FORMATTED_ADDRESS"] if "FORMATTED_ADDRESS" in dict_order_taker else ""
        
        additional_info = "CPF={}|NAME={}|ADDRESS={}".format(customer_document, customer_name, customer_address)
        order_taker.updateOrderProperties(pos_id, additionalinfo=additional_info)
    
    def save_order(self, pos_id):
        # type: (int) -> None
        model = sysactions.get_model(pos_id)
        order_taker = sysactions.get_posot(model)
        
        order_taker.storeOrder(pos_id)
    
    def update_order(self, pos_id, remote_order_id, order_id, order_trees):
        # type: (int, unicode, int, unicode) -> None
        model = sysactions.get_model(pos_id)
        order_taker = sysactions.get_posot(model)
        
        order_trees = json.loads(order_trees)
        order_trees = json.dumps({'data': order_trees})
        order_taker.setOrderCustomProperties({"RETRANSMIT_%s" % remote_order_id: order_trees}, order_id)
    
    def get_order_pict(self, pos_id, order_id):
        # type: (int, int) -> eTree.XML
        model = sysactions.get_model(pos_id)
        order_taker = sysactions.get_posot(model)
        
        return eTree.fromstring(order_taker.orderPicture(pos_id, order_id))
    
    def get_order_tree(self, pos_id, order_id, remote_order_id):
        # type: (int, int, int) -> eTree.XML
        model = sysactions.get_model(pos_id)
        order_taker = sysactions.get_posot(model)
        
        props = order_taker.getOrderCustomProperties(key="RETRANSMIT_%s" % remote_order_id, orderid=order_id)
        return eTree.XML(props).find("OrderProperty").get("value")
    
    def _print_danfe(self, model, data, order_id):
        
        if data == "":
            return
        
        current_printer = sysactions.get_used_service(model, "printer")
        default_error = "Error printing fiscal coupon for OrderId#{} - {}".format(order_id, current_printer)
        
        for i in range(self.printer_max_retries):
            
            retry_info = "{}/{}".format(i + 1, self.printer_max_retries)
            logger.info("Trying to print fiscal coupon for OrderId#{} - {}".format(order_id, retry_info))
            
            try:
                
                msg = self.mbcontext.MB_EasySendMessage(current_printer,
                                                        msgbus.TK_PRN_PRINT,
                                                        format=msgbus.FM_PARAM,
                                                        data=data,
                                                        timeout=10000000)  # type: msgbus.MBMessage
                if msg.token != msgbus.TK_SYS_ACK:
                    logger.error("{} - {}".format(default_error, msg.data))
                break
            
            except msgbus.MBTimeout as _:
                logger.error("{} - Printer service timeout".format(default_error))
            
            except msgbus.MBException as _:
                logger.error("{} - Printer service not found".format(default_error))
            
            time.sleep(self.printer_retry_time)
    
    def finalize_order(self, pos_id, order_id):
        # type: (int, int) -> None
        
        model = sysactions.get_model(pos_id)
        order_taker = sysactions.get_posot(model)
        
        self.prepare_order_state(model, order_id, order_taker, pos_id)
        self.default_quantity_fixer.fix_default_quantity(pos_id, order_id)
        self._do_order_total(order_id, order_taker, pos_id)
        available_tender_types = self.product_repository.get_tender_types()
        
        partner = OrderTakerWrapper._get_partner(order_id, order_taker)
        tender_type = self._get_tender_data(partner, order_id, order_taker, pos_id, available_tender_types)
        
        order_picture = order_taker.orderPicture(pos_id)
        due_amount = float(eTree.XML(order_picture).get("dueAmount"))
        due_amount = self._apply_voucher_tender(due_amount, order_id, order_taker, pos_id, available_tender_types)
        do_tender_response = order_taker.doTender(posid=pos_id, tenderid=tender_type, amount=due_amount,
                                                  donotclose=True)
        
        self._check_due_amount(do_tender_response, order_taker, pos_id, tender_type)
        self._check_empty_tender(do_tender_response, order_taker, pos_id, tender_type)
        
        tender_id = int(do_tender_response["tenderId"])
        self.fiscal_repository.add_payment_data(pos_id, order_id, tender_id, tender_type, due_amount, 0.0)
        self.fiscalize_order(do_tender_response, due_amount, model, order_id, order_taker, partner, pos_id)
    
    def fiscalize_order(self, do_tender_response, due_amount, model, order_id, order_taker, partner, pos_id):
        data = '\0'.join([str(pos_id), str(order_id)])
        ret = self.mbcontext.MB_EasySendMessage("FiscalWrapper", BusTokens.TK_FISCALWRAPPER_PROCESS_REQUEST,
                                                format=msgbus.FM_PARAM, data=data)
        if ret.token == msgbus.TK_SYS_ACK:
            if self._can_print_order(partner):
                print_thread = Thread(target=self._print_danfe, args=[model, ret.data, order_id])
                print_thread.daemon = True
                print_thread.start()
            
            update_tender_response = order_taker.doTender(posid=pos_id, tenderid=0, amount=due_amount, donotclose=False,
                                                          ordertenderid=do_tender_response["tenderId"])
            if round_half_away_from_zero(float(update_tender_response["dueAmount"]), 2) != 0.00:
                raise FiscalException("Error processing payment")
        else:
            logger.error("Error processing fiscal coupon: {}".format(ret.data))
            data_resp = ret.data.split("\0")
            fiscal_ok = data_resp[0]
            
            if fiscal_ok == "True":
                logger.info("Error printing fiscal coupon: {}".format(ret.data))
                update_tender_response = order_taker.doTender(posid=pos_id, tenderid=0, amount=due_amount,
                                                              donotclose=False,
                                                              ordertenderid=do_tender_response["tenderId"])
                if float(update_tender_response["dueAmount"]) != 0.0:
                    raise FiscalException("Error processing payment")
            else:
                retry_count = 0
                try:
                    retry_count_resp = order_taker.getOrderCustomProperties(key="RETRY_COUNT", orderid=order_id)
                    if retry_count_resp is not None:
                        retry_count_xml = eTree.XML(retry_count_resp)
                        order_property = retry_count_xml.find("OrderProperty")
                        if order_property is not None:
                            retry_count = int(order_property.get("value"))
                except OrderTakerException:
                    pass
                
                retry_count += 1
                order_taker.setOrderCustomProperty("RETRY_COUNT", str(retry_count))
                order_taker.clearTenders(pos_id)
                order_taker.storeOrder(pos_id)
                if retry_count >= 3:
                    raise FiscalException("Error processing fiscal coupon")
                
                reason = "Unknown error"
                if len(data_resp) > 1:
                    reason = data_resp[1]
                
                raise FiscalException(reason)
    
    @staticmethod
    def _check_due_amount(do_tender_response, order_taker, pos_id, tender_id):
        if round_half_away_from_zero(float(do_tender_response["dueAmount"]), 2) != 0.00:
            order_taker.clearTenders(pos_id)
            order_taker.storeOrder(pos_id)
            exception_message = "Error processing payment. DueAmount: {}. TenderId: {}" \
                .format(do_tender_response["dueAmount"], tender_id)
            raise PaymentException(exception_message,
                                   "$ERROR_PROCESSING_PAYMENT|{}|{}".format(do_tender_response["dueAmount"], tender_id))
    
    @staticmethod
    def _check_empty_tender(do_tender_response, order_taker, pos_id, tender_id):
        if "tenderId" not in do_tender_response:
            order_taker.clearTenders(pos_id)
            order_taker.storeOrder(pos_id)
            exception_message = "Error processing payment. Tender without TenderId. DueAmount: {}. TenderId: {}" \
                .format(do_tender_response["dueAmount"], tender_id)
            raise PaymentException(exception_message,
                                   "$ERROR_PROCESSING_PAYMENT|{}|{}".format(do_tender_response["dueAmount"], tender_id))
    
    @staticmethod
    def _do_order_total(order_id, order_taker, pos_id):
        try:
            order_taker.doTotal(pos_id)
        except OrderTakerException as ex:
            order_taker.clearTenders(pos_id)
            order_taker.storeOrder(pos_id)
            exception_message = "Error totalizing order. OrderId #{}. Exception: {}".format(order_id, ex.message)
            raise OrderException(exception_message, "$ERROR_TOTALIZING_ORDER|{}|{}".format(order_id, ex.message))
    
    @staticmethod
    def prepare_order_state(model, order_id, order_taker, pos_id):
        recall_order = True
        if sysactions.has_current_order(model):
            current_order = sysactions.get_current_order(model)
            current_order_id = current_order.get("orderId")
            if current_order_id == order_id:
                logger.info("Current order is the same order that we need")
                recall_order = False
            else:
                try:
                    message = "Storing current order to recall the order that we need. CurrentOrderId: {}; OrderId: {}"
                    logger.info(message.format(current_order_id, order_id))
                    order_taker.storeOrder(pos_id)
                except OrderTakerException:
                    pass
        else:
            logger.info("Has no current order in model")
        if recall_order:
            try:
                logger.info("Recalling the OrderId: {}".format(order_id))
                order_taker.recallOrder(pos_id, order_id)
            except OrderTakerException as ex:
                exception_message = "Error recalling order. OrderId #{}. Exception: {}".format(order_id, ex.message)
                raise OrderException(exception_message, "$ERROR_RECALLING_ORDER|{}|{}".format(order_id, ex.message))
    
    def _get_tender_data(self, partner, order_id, order_taker, pos_id, available_tender_types):
        tender_type = OrderTakerWrapper._get_tender_type(order_id, order_taker)
        tender_id = OrderTakerWrapper._get_tender_id_from_custom_property(order_id, order_taker)
        
        if not tender_id:
            if tender_type == "online":
                tender_id = OrderTakerWrapper._get_tender_id_from_database(available_tender_types, partner.lower())
            else:
                tender_id = self._payment_on_delivery()
            
            if not tender_id:
                exception_message = "TenderId not found for order#{}: " \
                                    "TenderType: {}; Partner: {}".format(order_id, tender_type, partner)
                order_taker.voidOrder(pos_id)
                raise PaymentException(exception_message, "$TENDER_ID_NOT_FOUND|{}|{}".format(tender_type, partner))
        
        logger.info("Obtained TenderId for OrderId#{}. TenderId: {}; TenderType: {}; Partner: {}"
                    .format(order_id, tender_id, tender_type, partner))
        
        return tender_id

    @staticmethod
    def _payment_on_delivery():
        return 128
    
    @staticmethod
    def _get_tender_type(order_id, order_taker):
        tender_type_prop = order_taker.getOrderCustomProperties(key="TENDER_TYPE", orderid=order_id)
        tender_type = eTree.XML(tender_type_prop).find("OrderProperty").get("value").lower()
        return tender_type
    
    @staticmethod
    def _get_partner(order_id, order_taker):
        partner_prop = order_taker.getOrderCustomProperties(key="PARTNER", orderid=order_id)
        partner = eTree.XML(partner_prop).find("OrderProperty").get("value")
        return partner
    
    @staticmethod
    def _get_tender_id_from_custom_property(order_id, order_taker):
        pos_tender_prop = order_taker.getOrderCustomProperties(key="POS_TENDER", orderid=order_id)
        pos_tender = eTree.XML(pos_tender_prop).find("OrderProperty")
        tender_id = None
        if pos_tender is not None:
            tender_id = int(pos_tender.get("value"))
        return tender_id
    
    @staticmethod
    def _get_tender_id_from_database(available_tender_types, partner):
        tender_id = None
        if partner in available_tender_types:
            tender_id = available_tender_types[partner]
        return tender_id
    
    def _apply_voucher_tender(self, due_amount, order_id, order_taker, pos_id, available_tender_types):
        if not self.sell_with_partner_price:
            return due_amount
        
        voucher_resp = order_taker.getOrderCustomProperties(key="PARTNER_COUPON_PRODUCT", orderid=order_id)
        voucher_value = eTree.XML(voucher_resp).find("OrderProperty")
        if voucher_value is not None:
            voucher_value = float(voucher_value.get("value"))
            if voucher_value > 0.0:
                tender_voucher_id = 200
                if tender_voucher_id not in available_tender_types.values():
                    order_taker.voidOrder(pos_id)
                    exception_message = "Invalid voucher tender id: {}".format(tender_voucher_id)
                    raise PaymentException(exception_message, "$INVALID_VOUCHER|{}".format(tender_voucher_id))
                
                do_tender_response = order_taker.doTender(posid=pos_id, tenderid=tender_voucher_id,
                                                          amount=float(voucher_value),
                                                          donotclose=True)
                self.fiscal_repository.add_payment_data(pos_id, order_id, int(do_tender_response["tenderId"]),
                                                        tender_voucher_id,
                                                        float(voucher_value), 0.0)
                due_amount = float(do_tender_response["dueAmount"])
        return due_amount
    
    def _can_print_order(self, partner):
        if partner == "app" and self.print_app_coupon is False:
            return False
        return True
    
    def cancel_order(self, pos_id, order_id):
        model = sysactions.get_model(pos_id)
        order_taker = sysactions.get_posot(model)
        
        try:
            self.fiscalization_cancel(order_id, order_taker, pos_id)
            order_taker.voidOrder(int(pos_id), 0, order_id, 0)
        except OrderTakerException as _:
            logger.exception("Error voiding OrderId#{}; PosId#{}".format(order_id, pos_id))
            raise
    
    def fiscalization_cancel(self, order_id, order_taker, pos_id):
        fiscalization_cancelled = False
        try:
            logger.info("Trying to cancel the fiscalization")
            fiscalization = order_taker.getOrderCustomProperties(key="FISCALIZATION_DATE", orderid=order_id)
            fiscalization = eTree.XML(fiscalization).find("OrderProperty").get("value")
            if fiscalization:
                data = "|".join([str(pos_id), str(order_id)])
                msg = self.mbcontext.MB_EasySendMessage("FiscalWrapper",
                                                        BusTokens.TK_FISCALWRAPPER_CANCEL_ORDER,
                                                        format=msgbus.FM_PARAM,
                                                        data=data)
                if msg.token == msgbus.TK_SYS_ACK:
                    fiscalization_cancelled = True
                else:
                    sysactions.show_messagebox(pos_id, message="$ERROR_CANCEL_FISCAL_ORDER|{}".format(msg.data))
        except (Exception, msgbus.MBTimeout, msgbus.MBException):
            pass
        finally:
            if fiscalization_cancelled:
                logger.info("Order fiscalization successfully cancelled by fiscalwrapper")
            else:
                logger.info("Cannot cancel the fiscalization by fiscalwrapper")
    
    @staticmethod
    def add_comments(pos_id, order_id, order_trees):
        model = sysactions.get_model(pos_id)
        order_taker = sysactions.get_posot(model)
        
        for line_number in range(1, len(order_trees) + 1):
            current_product = order_trees[line_number - 1].product
            if not current_product.comment:
                continue
            order_taker.addComment(line_number, '1', 0, current_product.part_code, current_product.comment)
    
    def _filter_customer_name(self, customer_name):
        try:
            msg = self.mbcontext.MB_LocateService(self.mbcontext.hv_service, 'Blacklist', maxretries=1)
            if msg:
                msg = self.mbcontext.MB_EasySendMessage("Blacklist", BusTokens.TK_BLACKLIST_FILTER_STRING,
                                                        msgbus.FM_PARAM, customer_name)
                if msg.token == msgbus.TK_SYS_ACK:
                    return msg.data
            return customer_name
        except msgbus.MBException:
            return customer_name
    
    def add_prep_time(self, pos_id, order_id):
        model = sysactions.get_model(pos_id)
        order_taker = sysactions.get_posot(model)
        order_type = order_taker.getOrderCustomProperties(key="ORDER_TYPE", orderid=order_id)
        order_property = eTree.XML(order_type).find("OrderProperty")
        if order_property is None:
            return
        
        order_type = order_property.get("value")
        if order_type != "A":
            return
        
        scheduled_delivery = order_taker.getOrderCustomProperties(key="SCHEDULE_TIME", orderid=order_id)
        scheduled_delivery = eTree.XML(scheduled_delivery).find("OrderProperty").get("value")
        time_delivery = iso8601.parse_date(scheduled_delivery)
        msg = self.mbcontext.MB_LocateService(self.mbcontext.hv_service, 'ProductionSystem', maxretries=1)
        if msg:
            ret = self.mbcontext.MB_EasySendMessage("ProductionSystem", BusTokens.TK_PROD_GET_ORDER_MAX_PREP_TIME,
                                                    format=msgbus.FM_PARAM, data=str(order_id))
            if ret.token == msgbus.TK_SYS_ACK and (ret.data and ret.data.lower() != "none"):
                prep_time = int(ret.data)
                if prep_time > 0:
                    time_to_start = time_delivery - datetime.timedelta(seconds=prep_time)
                    time_to_start = time_to_start.strftime('%Y-%m-%dT%H:%M:%SZ')
                    order_taker.setOrderCustomProperty(key="SCHEDULE_TIME", value=time_to_start, orderid=order_id)
    
    @staticmethod
    def set_order_custom_property(pos_id, order_id, key, value):
        model = sysactions.get_model(pos_id)
        order_taker = sysactions.get_posot(model)
        order_taker.setOrderCustomProperty(key=key, value=value, orderid=order_id)
    
    @staticmethod
    def get_order_custom_property(pos_id, order_id, key):
        model = sysactions.get_model(pos_id)
        order_taker = sysactions.get_posot(model)
        return order_taker.getOrderCustomProperties(key=key, orderid=order_id)
    
    @staticmethod
    def apply_discount(pos_id, amount):
        model = sysactions.get_model(pos_id)
        order_taker = sysactions.get_posot(model)
        order_taker.applyDiscount(1, amount, forcebyitem=1)
        
    def create_item(self, pos_id, item_id, qty):
        model = sysactions.get_model(pos_id)
        order_taker = sysactions.get_posot(model)
        order_taker.doSale(int(pos_id), item_id, 'DL', qty, self.apply_default_options)
