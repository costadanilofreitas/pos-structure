# -*- coding: utf-8 -*-

import json

from sysactions import action, get_model, get_posot, show_messagebox, close_asynch_dialog

from utilfunctions import compare_objects

from ..customer import Customer
from ..customer.model import AddCustomerRequest

dialog_id = None


@action
def delivery_address_information(pos_id, address_data):
    model = get_model(pos_id)
    pos_ot = get_posot(model)
    address_data_load = json.loads(address_data)
    _update_order_custom_properties(address_data_load, model, pos_id, pos_ot)

    customer_request = _create_customer_request(address_data_load)
    
    if customer_request.phone:
        customer = Customer().get_customer(customer_request.phone)
        if not customer:
            message = "$CUSTOMER_WILL_BE_INSERTED"
            confirmation = show_messagebox(pos_id, message, timeout=720000, buttons="$OK|$CANCEL")
            if confirmation == 1:
                return
        
            Customer().add_customer(customer_request)
            return
    
        customer_updated = compare_objects(customer_request, _create_customer_request_to_compare(json.loads(customer)))
        if not customer_updated:
            message = "$CUSTOMER_WILL_BE_UPDATED"
            confirmation = show_messagebox(pos_id, message, timeout=720000, buttons="$OK|$CANCEL")
            if confirmation == 1:
                return
            
            Customer().update_customer(customer_request)


def _create_customer_request(address_data_load):
    add_customer_request = AddCustomerRequest(
            address_data_load["CUSTOMER_PHONE"],
            address_data_load["CUSTOMER_DOC"],
            address_data_load["CUSTOMER_NAME"],
            address_data_load["POSTAL_CODE"],
            address_data_load["CITY"],
            address_data_load["STREET_NAME"],
            address_data_load["NEIGHBORHOOD"],
            address_data_load["STREET_NUMBER"],
            address_data_load["COMPLEMENT"],
            address_data_load["ADDRESS_REFERENCE"],
    )
    
    return add_customer_request


def _create_customer_request_to_compare(customer):
    add_customer_request = AddCustomerRequest(
            customer["phone"],
            customer["document"],
            customer["name"],
            customer["address"]["zip_code"],
            customer["address"]["city"],
            customer["address"]["street"],
            customer["address"]["neighborhood"],
            customer["address"]["number"],
            customer["address"]["complement"],
            customer["address"]["reference_point"]
    )
    return add_customer_request


@action
def zip_code_search(pos_id):
    global dialog_id
    dialog_id = show_messagebox(pos_id, "$SEARCHING_ZIP_CODE", buttons="", asynch=True, timeout=50000)
    
    
@action
def zip_code_search_finished(pos_id, error="false"):
    close_asynch_dialog(pos_id, dialog_id)
    if error == "true":
        show_messagebox(pos_id, "$ERROR_SEARCHING_ZIP_CODE", buttons="OK")


def _update_order_custom_properties(address_data_load, model, pos_id, pos_ot):
    for key, value in address_data_load.iteritems():
        if value == '':
            if model.find('.//OrderProperty[@key="{}"]'.format(key)) is not None:
                pos_ot.setOrderCustomProperty(key, 'clear')
        else:
            pos_ot.setOrderCustomProperty(key, value.encode('utf-8'))
            
    _update_order_properties(pos_id, pos_ot, model)
    
    
def _update_order_properties(pos_id, pos_ot, model):
    sale_type = model.find(".//Order").get("saleType")
    pos_ot.updateOrderProperties(pos_id, saletype=sale_type)
