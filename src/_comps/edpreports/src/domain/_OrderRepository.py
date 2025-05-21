# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

from typing import List  # noqa
from datetime import datetime  # noqa
from _Order import Order  # noqa


class OrderRepository(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_order(self, initial_date, end_date, pos, operator):
        # type: (datetime, datetime, int, int) -> List[Order]
        raise NotImplementedError()
