from enum import Enum


class TenderIdEnum(Enum):
    CASH = 0
    CREDIT_CARD = 1
    DEBIT_CARD = 2
    EXTERNAL_PAYMENT = 3
