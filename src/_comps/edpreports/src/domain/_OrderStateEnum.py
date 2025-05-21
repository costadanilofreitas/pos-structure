from enum import Enum


class OrderStateEnum(Enum):
    UNDEFINED = 0
    IN_PROGRESS = 1
    STORED = 2
    TOTALED = 3
    VOIDED = 4
    PAID = 5
    RECALLED = 6
    SYSTEM_VOIDED = 7
    ABANDONED = 8
