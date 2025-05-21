class ProductPart(object):
    def __init__(self, product_code, part_code, min_quantity, max_quantity, default_quantity):
        self.product_code = product_code
        self.part_code = part_code
        self.min_quantity = min_quantity
        self.max_quantity = max_quantity
        self.default_quantity = default_quantity
