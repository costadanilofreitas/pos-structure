from enum import IntEnum


class DeliveryEventTypes(IntEnum):
    ORDER_READY_TO_DELIVERY = 1
    LOGISTIC_DISPATCHED = 2
    LOGISTIC_DELIVERED = 3

