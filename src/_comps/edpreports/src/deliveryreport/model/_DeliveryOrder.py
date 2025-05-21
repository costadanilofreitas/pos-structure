import json


class DeliveryOrder(object):
    def __init__(self, order_json):
        order = json.loads(order_json)

        self.store_name = self._get_store_name(order)
        self.order_number = order.get("shortReference", "0")
        self.order_date = order.get("createAt", "2099-01-01T00:00:00.00000Z")
        self.items = order.get("items", [])
        self.total_price = order.get("totalPrice", "0.00")
        self.sub_total_price = order.get("subTotal", "0.00")
        self.delivery_fee = order.get("deliveryFee", "0.00")
        self.observation = self._get_custom_property(order, "observation")
        self.tenders = order.get("tenders", [])
        self.customer_name = self._get_custom_property(order, "customer_name")
        self.customer_doc = self._get_custom_property(order, "customer_doc")
        self.customer_phone = self._get_custom_property(order, "customer_phone")
        self.address = ""
        self.address_neighborhood = ""
        self.city = ""
        self.address_complement = ""
        self.postal_code = ""
        self.vouchers = {}
        
        if "pickup" in order and "address" in order["pickup"]:
            self.address = order["pickup"]["address"].get("formattedAddress", "")
            self.address_neighborhood = order.get("pickup").get("address").get("neighborhood", "")
            self.city = order.get("pickup").get("address").get("city", "")
            self.address_complement = order.get("pickup").get("address").get("complement", "")
            self.postal_code = order.get("pickup").get("address").get("postalCode", "")

        self._create_vouchers(order)

    def _create_vouchers(self, order):
        self.vouchers["ORDER"] = 0
        self.vouchers["TOTAL_ITEMS"] = 0
        self.vouchers["DELIVERY_FEE"] = 0
        
        if "vouchers" in order and "store" in order["vouchers"]:
            self._get_order_vouchers(order)
            self._get_total_items_vouchers(order)
            self._get_delivery_fee_vouchers(order)

    def _get_order_vouchers(self, order):
        if "order" in order["vouchers"]["store"]:
            self.vouchers["ORDER"] += order["vouchers"]["store"]["order"]
            
        if "order" in order["vouchers"]["partner"]:
            self.vouchers["ORDER"] += order["vouchers"]["partner"]["order"]

    def _get_total_items_vouchers(self, order):
        if "total_items" in order["vouchers"]["store"]:
            self.vouchers["TOTAL_ITEMS"] += order["vouchers"]["store"]["total_items"]
    
        if "total_items" in order["vouchers"]["partner"]:
            self.vouchers["TOTAL_ITEMS"] += order["vouchers"]["partner"]["total_items"]

    def _get_delivery_fee_vouchers(self, order):
        if "delivery_fee" in order["vouchers"]["store"]:
            self.vouchers["DELIVERY_FEE"] += order["vouchers"]["store"]["delivery_fee"]
    
        if "delivery_fee" in order["vouchers"]["partner"]:
            self.vouchers["DELIVERY_FEE"] += order["vouchers"]["partner"]["delivery_fee"]

    @staticmethod
    def _get_custom_property(order, key):
        if "custom_properties" in order:
            value = [x for x in order["custom_properties"] if x["key"] == key]
            if len(value) > 0:
                return value[0]["value"]
        
        return ""

    @staticmethod
    def _get_store_name(order):
        store_name = order["partner"]
        if "brand" in order:
            store_name += " - " + order["brand"]
    
        return store_name
