from datetime import datetime

from production.box import CustomParamPrepTimeBox
from production.model import ProductionOrder
from production.repository import ProductRepository
from timeutil import RealClock


class GetOrderMaxPrepTimeInteractor(object):
    def __init__(self, product_repository):
        # type: (ProductRepository) -> None
        self.product_repository = product_repository

    def execute(self, production_order):
        # type: (ProductionOrder) -> int
        production_order.display_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        custom_param_prep_time_box = CustomParamPrepTimeBox("", None, self.product_repository, RealClock())
        production_order = custom_param_prep_time_box.change_order(production_order)

        return production_order.max_prep_time
