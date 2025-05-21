import json
import os
from decimal import Decimal
from logging import Logger
from xml.etree.ElementTree import Element
from datetime import datetime
from xml.etree import cElementTree as eTree

import requests
from orderpump.jsonutil import DefaultJsonEncoder
from orderpump.model.exception import InvalidResponseCode, OrderNotFound
from orderpump.repository import OrderPictureRepository, ProductRepository


class PumpOrderService(object):
    def __init__(self, store_id, pump_url, api_key, order_picture_repository, product_repository, logger):
        # type: (str, str, str, OrderPictureRepository, ProductRepository, Logger) -> None
        self.store_id = store_id
        self.pump_url = pump_url
        self.api_key = api_key
        self.order_picture_repository = order_picture_repository
        self.product_repository = product_repository
        self.logger = logger

    def send(self, order_id):
        # type: (int) -> None
        order_picture = self.order_picture_repository.get_order_picture(order_id)
        if order_picture == '':
            raise OrderNotFound()
        order_xml = eTree.XML(order_picture)
        order_dict = self.convert_order_picture_to_json(order_xml.find("Order"))
        self.send_order(order_dict)

    def convert_order_picture_to_json(self, order_picture):
        # type: (Element) -> dict
        payload = {
            "store-code": str(self.store_id),
            "order-code": order_picture.get("orderId")
        }
        session_id = order_picture.get("sessionId")
        for session_data in session_id.split(","):
            key_data = session_data.split("=")
            if key_data[0] == "user":
                payload["pos-user-id"] = key_data[1]

        if order_picture.get("exemptionCode"):
            payload["exemption"] = int(order_picture.get("exemptionCode"))
        if order_picture.get("posId"):
            payload["pos-code"] = order_picture.get("posId")
        else:
            for session_data in session_id.split(","):
                key_data = session_data.split("=")
                if key_data[0] == "pos":
                    payload["pos-code"] = key_data[1]

        period = order_picture.get("businessPeriod")
        period = datetime.strptime(period, "%Y%m%d")
        payload["business-dt"] = period.strftime("%Y-%m-%d")
        payload["session"] = session_id
        payload["originator-code"] = order_picture.get("originatorId")
        payload["pod-type"] = order_picture.get("podType")
        payload["state-id"] = int(order_picture.get("stateId"))
        payload["type-id"] = int(order_picture.get("typeId"))
        payload["sale-type-id"] = int(order_picture.get("saleType"))
        payload["price-list"] = order_picture.get("priceList")
        payload["price-basis"] = order_picture.get("priceBasis")
        payload["total-amount"] = float(order_picture.get("totalAmount") or 0)
        payload["total-after-discount"] = float(order_picture.get("totalAfterDiscount") or 0)
        payload["total-gross"] = float(order_picture.get("totalGross") or 0)
        payload["total-tender"] = float(order_picture.get("totalTender") or 0)
        payload["total-gift"] = float(0)
        payload["change"] = float(order_picture.get("change") or 0)
        payload["due-amount"] = float(order_picture.get("dueAmount") or 0)
        payload["tax-total"] = float(order_picture.get("taxTotal") or 0)
        payload["discount-amount"] = float(order_picture.get("discountAmount") or 0)
        payload["order-discount-amount"] = float(order_picture.get("orderDiscountAmount") or 0)
        payload["tip"] = float(order_picture.get("tip") or 0)
        payload["tax-applied"] = float(order_picture.get("taxTotal") or 0)
        payload["discount-applied"] = order_picture.get("discountsApplied")
        payload["creation-dttm"] = order_picture.get("createdAt")
        payload["order-picture-sale-lines"] = []
        payload["order-picture-tenders"] = []
        for sale_line in order_picture.findall("SaleLine"):
            sale_line_payload = {"order-picture-id": int(order_picture.get("orderId")),
                                 "line-number": int(sale_line.get("lineNumber")), "level": int(sale_line.get("level")),
                                 "plu": sale_line.get("partCode"), "menu-item-code": sale_line.get("itemId"),
                                 "item-type": sale_line.get("itemType"),
                                 "part-code": sale_line.get("partCode"),
                                 "product": sale_line.get("productName"),
                                 "multiplied-qty": Decimal(sale_line.get("multipliedQty")), 
                                 "qty": Decimal(sale_line.get("qty")),
                                 "inc-qty": Decimal(sale_line.get("incQty")), 
                                 "dec-qty": Decimal(sale_line.get("decQty"))}
            if sale_line.get("defaultQty"):
                sale_line_payload["default-qty"] = Decimal(sale_line.get("defaultQty"))
            if sale_line.get("addedQty"):
                sale_line_payload["added-qty"] = Decimal(sale_line.get("addedQty"))
            if sale_line.get("subQty"):
                sale_line_payload["sub-qty"] = Decimal(sale_line.get("subQty"))
            if sale_line.get("chosenQty"):
                sale_line_payload["chosen-qty"] = Decimal(sale_line.get("chosenQty"))
            sale_line_payload["comment"] = []
            for comment in sale_line.findall("Comment"):
                sale_line_payload["comment"].append(comment.get("comment"))

            sale_line_payload["category-description"] = \
                self.product_repository.get_category(int(sale_line.get("partCode")))
            sale_line_payload["sub-category-description"] = \
                self.product_repository.get_sub_category(int(sale_line.get("partCode")))
            sale_line_payload["item-price"] = float(sale_line.get("itemPrice", "0"))
            sale_line_payload["unit-price"] = float(sale_line.get("unitPrice", "0"))
            sale_line_payload["added-unit-price"] = float(sale_line.get("addedUnitPrice", "0"))
            sale_line_payload["sub-unit-price"] = float(sale_line.get("subUnitPrice", "0"))
            sale_line_payload["price-key"] = sale_line.get("priceKey")
            payload["order-picture-sale-lines"].append(sale_line_payload)

        for tender_line in order_picture.findall("TenderHistory/Tender"):
            tender_payload = {"order-picture-id": int(order_picture.get("orderId")),
                              "tender-type": tender_line.get("tenderType"),
                              "tender-amount": float(tender_line.get("tenderAmount", "0")),
                              "reference-amount": float(tender_line.get("tenderAmount", "0")),
                              "change-amount": float(tender_line.get("change", "0"))}
            payload["order-picture-tenders"].append(tender_payload)
            if tender_line.get("tip"):
                tender_payload["tip"] = float(tender_line.get("tip"))
            
        return payload

    def send_order(self, order_dict):
        # type: (dict) -> None
        data = json.dumps(order_dict, cls=DefaultJsonEncoder).encode("UTF-8")
        self.logger.debug("Json that will be sent: {}".format(data))
        headers = {
            'Accept': 'application/json',
            'Content-type': 'application/json',
            'x-api-key': self.api_key
        }
        response = requests.post(self.pump_url,
                                 headers=headers,
                                 data=data,
                                 timeout=30,
                                 verify=False)
        if response.status_code != 200:
            self.logger.error("Invalid response code from BOH: {} - {}".format(response.status_code, response.content))
            raise InvalidResponseCode(response.status_code)
