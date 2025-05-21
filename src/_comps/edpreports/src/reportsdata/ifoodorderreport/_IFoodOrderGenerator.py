import json
from commons.report import Generator


class IFoodOrderGenerator(Generator):
    def __init__(self, order_json):
        self.order_json = order_json

    def generate_data(self):
        return json.loads(self.order_json)
