# -*- coding: utf-8 -*-

from json import JSONEncoder

from application.apimodel import CustomParam, Item, Order
from application.customexception import ValidationException


class ApiModelJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ValidationException):
            return {
                "errorCode": obj.error_code,
                "localizedErrorMessage": obj.localized_error_message
            }

        if isinstance(obj, Order):
            order_dict = {
                "id": obj.id,
                "items": obj.items,
                "receiveTime": obj.receive_time.strftime("%Y-%m-%dT%H:%M:%SZ") if obj.receive_time is not None else None,
                "customerName": obj.customer_name,
                "clientName": obj.customer_name,
                "businessPeriod": obj.business_period,
                "partner": obj.partner,
                "shortReference": obj.short_reference,
                "orderStatus": obj.order_status,
                "remoteId": obj.remote_id,
                "status": obj.status,
                "customProps": obj.custom_properties,
                "total": obj.total
            }
            if obj.pickup_time is not None:
                order_dict["pickupTime"] = obj.pickup_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            if obj.originator_id is not None:
                order_dict["originatorID"] = obj.originator_id

            # address data
            if obj.city is not None:
                order_dict["city"] = obj.city
            if obj.complement is not None:
                order_dict["complement"] = obj.complement
            if obj.address is not None:
                order_dict["address"] = obj.address
            if obj.neighborhood is not None:
                order_dict["neighborhood"] = obj.neighborhood
            if obj.postal is not None:
                order_dict["postal"] = obj.postal
            if obj.reference is not None:
                order_dict["reference"] = obj.reference
            if obj.state is not None:
                order_dict["state"] = obj.state

            return order_dict

        if isinstance(obj, Item):
            return {
                "partCode": obj.part_code,
                "context": obj.context,
                "productName": obj.product_name,
                "productType": obj.product_type,
                "quantity": obj.quantity,
                "defaultQuantity": obj.default_quantity,
                "sons": map(lambda x: self.default(x), obj.sons)
            }

        if isinstance(obj, CustomParam):
            return {
                "key": obj.key,
                "value": obj.value,
            }

        return super(ApiModelJsonEncoder, self).default(obj)
