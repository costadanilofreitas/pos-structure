from typing import List  # noqa
from ._CustomOrderProperty import CustomOrderProperty  # noqa
import math


class Order(object):
    def __init__(self, order_id, total_gross, tip, pos_id, custom_order_properties, due_amount):
        # type: (str, float, float, str, List[CustomOrderProperty], float) -> None
        self.__order_id = order_id
        self.__total_gross = total_gross
        self.__tip = tip
        self.__pos_id = pos_id
        self.__custom_order_properties = custom_order_properties
        self.__due_amount = due_amount

    @property
    def order_id(self):
        # type: () -> str
        return self.__order_id

    @property
    def total_gross(self):
        # type: () -> float
        return self.__total_gross

    @property
    def tip(self):
        # type: () -> float
        return self.total_amount

    @property
    def pos_id(self):
        # type: () -> str
        return self.__pos_id

    @property
    def tip_percentage(self):
        # type: () -> float
        tip_percentage = (self.__tip * 100) / self.__total_gross
        return math.floor(tip_percentage * 100)/100.0

    @property
    def custom_order_properties(self):
        # type: () -> List[CustomOrderProperty]
        return self.__custom_order_properties

    def get_custom_property_by_key(self, key):
        custom_properties = filter(lambda c_o: c_o.key == key, self.custom_order_properties)
        if len(custom_properties) > 0:
            return custom_properties[0].value

        return None

    @property
    def due_amount(self):
        # type: () -> float
        return self.__due_amount
