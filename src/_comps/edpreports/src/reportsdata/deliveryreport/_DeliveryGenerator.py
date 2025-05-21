from commons.report import Generator
from deliveryreport import DeliveryReport
from dto import DeliveryHeaderDto, DeliveryBodyDto, DeliveryGeneratorDto


class DeliveryGenerator(Generator):
    def __init__(self, order_repository, product_repository, order_id):
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.order_id = order_id

    def generate_data(self):
        delivery_report = DeliveryReport(self.order_repository, self.product_repository)
        order = delivery_report.get_delivery_order(self.order_id)
        products = delivery_report.get_products()
        header = DeliveryHeaderDto(order)
        body = DeliveryBodyDto(order)
        return DeliveryGeneratorDto(header, body, products)
