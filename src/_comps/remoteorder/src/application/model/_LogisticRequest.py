class LogisticRequest:
    def __init__(self, order_id, adapter, store_id, short_reference, delivery_location, customer):
        # type: (str, str, str, str, LogisticRequestLocation, LogisticRequestCustomer) -> None
        
        self.order_id = order_id
        self.adapter = adapter
        self.store_id = store_id
        self.short_reference = short_reference
        self.delivery_location = delivery_location
        self.customer = customer
        
        
class LogisticRequestLocation:
    def __init__(self):
        # type: () -> None
        
        self.latitude = ""
        self.longitude = ""
        self.street = ""
        self.number = ""
        self.neighborhood = ""
        self.city = ""
        self.state = ""
        self.cep = ""
        self.country = ""
        self.complement = ""


class LogisticRequestCustomer:
    def __init__(self):
        # type: () -> None
        
        self.name = ""
        self.phone = ""
