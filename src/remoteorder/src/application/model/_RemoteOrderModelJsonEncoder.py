# -*- coding: utf-8 -*-

from json import JSONEncoder

from application.customexception import OrderError, StoreClosedException

from ._OrderItem import OrderItem
from ._PriceWarning import PriceWarning
from ._ProcessedOrder import ProcessedOrder
from ._Store import Store
from ._StoreStatusHistory import StoreStatusHistory
from ._LogisticRequest import LogisticRequest, LogisticRequestLocation, LogisticRequestCustomer
from ._LogisticCancelRequest import LogisticCancelRequest
from ._LogisticConfirmRequest import LogisticConfirmRequest
from ._OrderReadyToDeliveryRequest import OrderReadyToDeliveryRequest
from ._OrderProducedRequest import OrderProducedRequest
from ._DeliveryConfirm import DeliveryConfirm


class RemoteOrderModelJsonEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, PriceWarning):
            return {
                "remoteOrderId": o.remote_order_id,
                "remoteOrderItemsValue": o.remote_order_items_value,
                "localOrderItemsValue": o.local_order_items_value
            }

        if isinstance(o, StoreStatusHistory):
            return {
                "id": o.id,
                "operator": o.operator,
                "status": o.status
            }

        if isinstance(o, Store):
            return {
                "id": o.id,
                "name": o.name,
                "status": o.status
            }

        if isinstance(o, StoreClosedException):
            return {
                "remoteOrderId": o.remote_order_id
            }

        if isinstance(o, ProcessedOrder):
            return {
                "id": o.remote_order_id,
                "localOrderId": o.local_order_id,
                "items": o.items,
                "hasError": o.has_error or False,
                "code": o.code or '',
                "errorMessage": o.error_message or ''
            }

        if isinstance(o, OrderItem):
            return {
                "productName": o.product_name,
                "productType": o.product_type,
                "quantity": o.quantity,
                "partCode": o.part_code,
                "parts": o.parts
            }

        if isinstance(o, OrderError):
            return {
                "id": o.remote_order_id,
                "code": o.error_code,
                "errorMessage": o.error_message
            }

        if isinstance(o, LogisticRequest):
            return {
                "orderId": o.order_id,
                "adapter": o.adapter,
                "storeId": o.store_id,
                "shortReference": o.short_reference,
                "deliveryLocation": o.delivery_location,
                "customer": o.customer
            }

        if isinstance(o, LogisticRequestCustomer):
            return {
                "name": o.name,
                "phone": o.phone
            }

        if isinstance(o, LogisticRequestLocation):
            return {
                "latitude": o.latitude,
                "longitude": o.longitude,
                "street": o.street,
                "number": o.number,
                "neighborhood": o.neighborhood,
                "city": o.city,
                "state": o.state,
                "cep": o.cep,
                "country": o.country,
                "complement": o.complement
            }

        if isinstance(o, LogisticCancelRequest):
            return {
                "logisticId": o.logistic_id,
                "storeId": o.store_id,
                "reason": o.reason
            }

        if isinstance(o, LogisticConfirmRequest):
            return {
                "id": o.remote_order_id,
                "adapterName": o.adapter_name,
                "adapterLogisticId": o.adapter_logistic_id,
                "isDeliveredByStore": o.is_delivery_by_store,
                "courierName": o.courier_name
            }

        if isinstance(o, OrderReadyToDeliveryRequest):
            return {
                "orderId": o.remote_order_id,
                "producedAt": o.produced_at,
                "readyToDeliveryAt": o.ready_to_delivery_at
            }

        if isinstance(o, OrderProducedRequest):
            return {
                "id": o.remote_order_id,
                "storeId": o.store_id,
                "fiscalXml": o.fiscal_xml,
                "items": o.items,
                "producing": o.producing
            }

        if isinstance(o, DeliveryConfirm):
            return {
                "id": o.id,
                "logisticId": o.logistic_id
            }

        return super(RemoteOrderModelJsonEncoder, self).default(o)
