class DeliveryBodyDto(object):
    def __init__(self, order):
        # type: (object) -> ()
        self.items = order.items
        self.total_price = order.total_price
        self.sub_total_price = order.sub_total_price
        self.delivery_fee = order.delivery_fee
        self.observation = order.observation
        self.tenders = order.tenders
        self.customer_name = order.customer_name
        self.customer_doc = order.customer_doc
        self.customer_phone = order.customer_phone
        self.address = order.address
        self.address_neighborhood = order.address_neighborhood
        self.city = order.city
        self.address_complement = order.address_complement
        self.postal_code = order.postal_code
        self.vouchers = order.vouchers
