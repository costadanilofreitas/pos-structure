from ._DeliveryHeaderDto import DeliveryHeaderDto
from ._DeliveryBodyDto import DeliveryBodyDto


class DeliveryGeneratorDto(object):
    def __init__(self, header, body, products):
        # type: (DeliveryHeaderDto, DeliveryBodyDto, object) -> ()
        self.header = header
        self.body = body
        self.products = products
