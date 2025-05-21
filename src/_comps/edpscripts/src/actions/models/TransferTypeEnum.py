# -*- coding: utf-8 -*-
from enum import Enum


class TransferType(Enum):
    INITIAL_AMOUNT = 1
    TRANSFER_SKIM = 2
    TRANSFER_CASH_IN = 3
    TRANSFER_CASH_OUT = 4
    FINAL_AMOUNT = 5
    DECLARED_AMOUNT = 6
