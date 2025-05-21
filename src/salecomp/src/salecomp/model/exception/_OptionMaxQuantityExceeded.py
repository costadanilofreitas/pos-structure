class OptionMaxQuantityExceeded(Exception):
    def __init__(self, parent_part_code, option_part_code, max_quantity, tried_quantity):
        self.parent_part_code = parent_part_code
        self.option_part_code = option_part_code
        self.max_quantity = max_quantity
        self.tried_quantity = tried_quantity
