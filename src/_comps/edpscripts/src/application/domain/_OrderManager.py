from abc import ABCMeta, abstractmethod


class OrderManager(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def store_order(self, pos_id):
        # type: (str) -> None
        raise NotImplementedError()

    @abstractmethod
    def recall_order(self, pos_id, order_id):
        # type -> (str) -> None
        raise NotImplementedError()

    @abstractmethod
    def change_line_seat(self, pos_id, sale_line, seat_number):
        # type -> (str, SaleLine, int) -> str
        raise NotImplementedError()

    @abstractmethod
    def get_current_order_state(self, pos_id):
        # type -> (str) -> str
        raise NotImplementedError()
