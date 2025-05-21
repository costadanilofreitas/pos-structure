# -*- coding: utf-8 -*-

import json
import logging
import sys

import iso8601
import six
from application.customexception import InvalidJsonException
from application.model import RemoteOrder, Tender, OrderItem, CustomProperty, PickUpInfo, Address
from application.repository import ProductRepository

logger = logging.getLogger("RemoteOrder")


class RemoteOrderParser(object):
    def __init__(self, product_repository, use_delivery_fee):
        # type: (ProductRepository, bool) -> None
        self.product_repository = product_repository
        self.use_delivery_fee = use_delivery_fee

    def parse_order(self, input_json):
        # type: (unicode) -> RemoteOrder
        try:
            parsed_json = json.loads(input_json)  # type: dict
        except ValueError as ex:
            raise six.reraise(InvalidJsonException, InvalidJsonException(ex.message, input_json), sys.exc_info()[2])

        try:
            self._validate_json_structure(parsed_json)
        except InvalidJsonException as ex:
            ex.invalid_json = input_json
            raise six.reraise(InvalidJsonException, InvalidJsonException(ex.message, input_json), sys.exc_info()[2])

        remote_order = self._build_remote_order(parsed_json)

        return remote_order

    def minimum_parse(self, input_json):
        # type: (unicode) -> RemoteOrder
        try:
            parsed_json = json.loads(input_json)  # type: dict
        except ValueError as ex:
            raise six.reraise(InvalidJsonException, InvalidJsonException(ex.message, input_json), sys.exc_info()[2])

        remote_order = self._minimum_build(parsed_json)

        return remote_order

    def parse_pickup_order(self, input_json):
        try:
            parsed_json = json.loads(input_json)  # type: dict
        except ValueError as ex:
            raise six.reraise(InvalidJsonException, InvalidJsonException(ex.message, input_json), sys.exc_info()[2])

        if "id" not in parsed_json:
            raise InvalidJsonException("Json without id tag", None)

        if "pickup" not in parsed_json:
            raise InvalidJsonException("Json without pickup tag", None)

        json_pickup = parsed_json["pickup"]

        remote_order = RemoteOrder()
        remote_order.id = parsed_json["id"]
        remote_order.pickup = PickUpInfo()

        if "time" in json_pickup and json_pickup["time"]:
            remote_order.pickup.time = iso8601.parse_date(json_pickup["time"])

        return remote_order

    def _validate_json_structure(self, parsed_json):
        # type: (dict) -> None

        if "id" not in parsed_json:
            raise InvalidJsonException("Json without id tag", None)

        if "code" not in parsed_json:
            raise InvalidJsonException("Json without code tag", None)

        if "createAt" not in parsed_json:
            raise InvalidJsonException("Json without createAt tag", None)

        if "partner" not in parsed_json:
            raise InvalidJsonException("Json without partner tag", None)

        if parsed_json["partner"].lower() not in self.product_repository.get_tender_types():
            message = "Invalid partner: {}; Available Partners: {}".format(parsed_json["partner"],
                                                                           self.product_repository.get_tender_types())
            logger.error(message)
            raise InvalidJsonException(message, None)

        if "shortReference" not in parsed_json:
            raise InvalidJsonException("Json without shortReference tag", None)

        try:
            iso8601.parse_date(parsed_json["createAt"])
        except:
            raise InvalidJsonException("Invalit createAt", None)

        if "items" not in parsed_json:
            raise InvalidJsonException("Json without items tag", None)

        self._validate_json_items(parsed_json["items"])

        if "tenders" not in parsed_json:
            raise InvalidJsonException("Json without tenders tag", None)

        self._validate_json_tenders(parsed_json["tenders"])

        if "pickup" not in parsed_json:
            raise InvalidJsonException("Json without pickup tag", None)

        self._validate_json_pickup(parsed_json["pickup"])

    def _validate_json_items(self, json_items):
        if not json_items:
            raise InvalidJsonException("Json with empty items tag", None)

        for json_item in json_items:
            if "partCode" not in json_item:
                raise InvalidJsonException("Items without partCode", None)

            if "quantity" not in json_item:
                raise InvalidJsonException("Items without quantity", None)

            if "parts" in json_item:
                json_parts = json_item["parts"]
                if json_parts:
                    self._validate_json_items(json_item["parts"])

    def _validate_json_tenders(self, json_tenders):
        if not json_tenders:
            raise InvalidJsonException("Json with empty tenders tag", None)

        for json_tender in json_tenders:
            if "prepaid" not in json_tender:
                raise InvalidJsonException("Tender without prepaid", None)

            if json_tender["prepaid"] not in (True, False, "true", "false"):
                raise InvalidJsonException("Invalid tender prepaid: {0}".format(json_tender["prepaid"]), None)

            if "value" not in json_tender:
                raise InvalidJsonException("Tender without value", None)

    @staticmethod
    def _validate_json_pickup(json_pickup):
        pickup_time = json_pickup.get("time")
        if pickup_time:
            try:
                iso8601.parse_date(pickup_time)
            except iso8601.ParseError:
                raise InvalidJsonException("Invalid Pickup.time", None)

        pickup_type = json_pickup.get("type")
        if pickup_type and pickup_type not in ["delivery", "eat_in", "take_out", "drive_thru"]:
            raise InvalidJsonException("Invalid Pickup.type", None)

    def _build_remote_order(self, parsed_json):
        # type: (dict) -> RemoteOrder
        remote_order = RemoteOrder()
        remote_order.id = parsed_json["id"]
        remote_order.code = parsed_json["code"]
        remote_order.partner = parsed_json["partner"]
        remote_order.short_reference = parsed_json["shortReference"]
        remote_order.created_at = iso8601.parse_date(parsed_json["createAt"])
        remote_order.tenders = self._parse_tenders(parsed_json["tenders"])
        remote_order.items = self._parse_order_item(parsed_json["items"])
        remote_order.originator_id = parsed_json.get("originalId")
        remote_order.delivery_fee = float(parsed_json.get("deliveryFee", 0)) if self.use_delivery_fee else 0
        remote_order.sub_total = parsed_json.get("subTotal", 0)
        remote_order.need_logistics = str(parsed_json.get("needLogistics", "false")).lower() == "true"
        
        if "custom_properties" in parsed_json:
            brand = parsed_json.get("brand")
            remote_order.custom_properties = self._parse_custom_properties(parsed_json["custom_properties"],
                                                                           remote_order.partner,
                                                                           brand,
                                                                           remote_order.need_logistics)
        else:
            remote_order.custom_properties = {}

        remote_order.pickup = self._parse_pickup(parsed_json["pickup"])
        self._get_order_discounts(parsed_json, remote_order)

        return remote_order

    def _minimum_build(self, parsed_json):
        # type: (dict) -> RemoteOrder
        remote_order = RemoteOrder()
        if 'id' in parsed_json:
            remote_order.id = parsed_json["id"]
        if 'code' in parsed_json:
            remote_order.code = parsed_json["code"]
        if 'partner' in parsed_json:
            remote_order.partner = parsed_json["partner"]
        if 'shortReference' in parsed_json:
            remote_order.short_reference = parsed_json["shortReference"]
        if 'createAt' in parsed_json:
            remote_order.created_at = iso8601.parse_date(parsed_json["createAt"])
        if 'originalId' in parsed_json:
            remote_order.originator_id = parsed_json.get("originalId")

        remote_order.need_logistics = parsed_json.get("needLogistics", "false") == "true"
        
        if "custom_properties" in parsed_json:
            brand = parsed_json.get("brand")
            remote_order.custom_properties = self._parse_custom_properties(parsed_json["custom_properties"],
                                                                           parsed_json["partner"],
                                                                           brand,
                                                                           remote_order.need_logistics)
        else:
            remote_order.custom_properties = {}
        remote_order.pickup = self._parse_pickup(parsed_json["pickup"])
        return remote_order

    def _parse_tenders(self, json_tenders):
        # type: (list) -> list
        all_tenders = []
        for json_tender in json_tenders:
            tender = Tender()
            if (isinstance(json_tender["prepaid"], bool) and json_tender["prepaid"]) or json_tender["prepaid"] == "true":
                tender.type = "online"

            tender.value = json_tender["value"]

            all_tenders.append(tender)
        return all_tenders

    def _parse_order_item(self, json_order_items):
        # type: (list) -> list
        all_order_items = []
        for json_item in json_order_items:  # type: dict
            order_item = OrderItem()
            order_item.part_code = json_item["partCode"]
            order_item.price = json_item.get("price", None)
            order_item.quantity = int(json_item["quantity"])
            order_item.comment = json_item.get("observation", "")
            if order_item.comment is None:
                order_item.comment = ""
            order_item.comment = order_item.comment.encode('utf-8')
            if "parts" in json_item and json_item["parts"] is not None:
                order_item.parts = self._parse_order_item(json_item["parts"])
            else:
                order_item.parts = []

            all_order_items.append(order_item)

        return all_order_items

    def _parse_custom_properties(self, json_custom_properties, partner, brand, need_logistics):
        # type: (list) -> dict
        all_custom_properties = {}

        for json_custom_property in json_custom_properties:
            if json_custom_property["value"]:
                key = json_custom_property["key"].upper()
                value = json_custom_property["value"]
                if key == "SCHEDULE_TIME":
                    value = iso8601.parse_date(json_custom_property["value"])
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                
                custom_property = self._create_custom_property(key, value)
                all_custom_properties[key] = custom_property

        custom_property = self._create_custom_property("PARTNER", partner)
        all_custom_properties["PARTNER"] = custom_property
        
        if brand:
            custom_property = self._create_custom_property("BRAND", brand)
            all_custom_properties["BRAND"] = custom_property

        if "STORE_NAME" not in all_custom_properties:
            custom_property = self._create_custom_property("STORE_NAME", partner)
            all_custom_properties["STORE_NAME"] = custom_property
            
        custom_property = self._create_custom_property("NEED_LOGISTICS", need_logistics)
        all_custom_properties["NEED_LOGISTICS"] = custom_property

        return all_custom_properties

    @staticmethod
    def _create_custom_property(key, value):
        custom_property = CustomProperty()
        custom_property.key = key
        custom_property.value = value

        return custom_property

    def _parse_pickup(self, json_pickup):
        # type: (dict) -> PickUpInfo
        pickup_info = PickUpInfo()

        if "time" in json_pickup and json_pickup["time"]:
            pickup_info.time = iso8601.parse_date(json_pickup["time"])

        if "type" in json_pickup and json_pickup["type"] is not None:
            pickup_info.type = json_pickup["type"]
        else:
            pickup_info.type = "delivery"

        pickup_info.company = json_pickup.get("company")
        if "address" in json_pickup:
            pickup_info.address = self._parse_address(json_pickup["address"])

        return pickup_info

    @staticmethod
    def _get_order_discounts(parsed_json, remote_order):
        remote_order.discount_amount = 0
        vouchers = parsed_json.get("vouchers")
        if not vouchers:
            return
        store_discount = vouchers.get("store")
        if not store_discount:
            return
        for discount_type in store_discount:
            discount_value = float(store_discount.get(discount_type))
            remote_order.discount_amount += discount_value
                

    @staticmethod
    def _parse_address(json_address):
        # type: (dict) -> Address
        address = Address()

        if not json_address:
            return address

        if "streetName" in json_address:
            address.streetName = json_address["streetName"]

        if "streetNumber" in json_address:
            address.streetNumber = json_address["streetNumber"]

        if "formattedAddress" in json_address:
            address.formattedAddress = json_address["formattedAddress"]

        if "complement" in json_address:
            address.complement = json_address["complement"]

        if "neighborhood" in json_address:
            address.neighborhood = json_address["neighborhood"]

        if "reference" in json_address:
            address.reference = json_address["reference"]

        if "postalCode" in json_address:
            address.postalCode = json_address["postalCode"]

        if "city" in json_address:
            address.city = json_address["city"]

        if "state" in json_address:
            address.state = json_address["state"]

        if "country" in json_address:
            address.country = json_address["country"]

        if "latitude" in json_address:
            address.latitude = json_address["latitude"]

        if "longitude" in json_address:
            address.longitude = json_address["longitude"]

        return address
