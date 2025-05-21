
class OperatorTip(object):
    def __init__(self, operator, service_id, default_unit_price, tip_portion):
        # type: (str, int, float, float) -> None
        self.operator = operator
        self.service_id = service_id
        self.default_unit_price = round(default_unit_price, 2)
        self.tip_portion = tip_portion
