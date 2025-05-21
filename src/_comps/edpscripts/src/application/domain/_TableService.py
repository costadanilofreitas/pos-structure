from abc import ABCMeta, abstractmethod

from ._Order import Order  # noqa
from typing import List, Optional, Union  # noqa
from ._Table import Table  # noqa


class TableService(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def list_tables(self, pos_id):
        # type: (Union[int, str]) -> List[Table]
        raise NotImplementedError()

    @abstractmethod
    def start_service(self, pos_id, table_id, seats, tab_id=""):
        # type: (Union[int, str], str, int, Optional[str]) -> str
        raise NotImplementedError()

    @abstractmethod
    def recall_service(self, pos_id, table_id):
        # type: (Union[int, str], str) -> str
        raise NotImplementedError()

    @abstractmethod
    def store_service(self, pos_id, table_id):
        # type: (Union[int, str], str) -> None
        raise NotImplementedError()

    @abstractmethod
    def create_order(self, pos_id, table_id):
        # type: (Union[int, str], str) -> None
        raise NotImplementedError()

    @abstractmethod
    def get_table_picture(self, pos_id, table_id):
        # type: (Union[int, str], str) -> str
        raise NotImplementedError()

    @abstractmethod
    def get_selected_table(self, pos_id):
        # type: (Union[int, str]) -> Table
        raise NotImplementedError()

    @abstractmethod
    def get_table(self, pos_id, table_id):
        # type: (Union[int, str], str) -> Table
        raise NotImplementedError()

    @abstractmethod
    def do_total_table(self, pos_id, table_id, tip_rate=None, seat_distribution=None):
        # type: (Union[int, str], str, Optional[str], Optional[bool]) -> str
        raise NotImplementedError()

    @abstractmethod
    def reopen_table(self, pos_id, table_id):
        # type: (Union[int, str], str) -> str
        raise NotImplementedError()

    @abstractmethod
    def close_table(self, pos_id, table_id):
        # type: (Union[int, str], str) -> str
        raise NotImplementedError()

    @abstractmethod
    def set_table_available(self, pos_id, table_id):
        # type: (Union[int, str], str) -> None
        raise NotImplementedError()

    @abstractmethod
    def get_current_table_id(self, pos_id):
        # type: (Union[int, str]) -> str
        raise NotImplementedError()

    @abstractmethod
    def clear_service_tenders(self, pos_id, table_id):
        # type: (Union[int, str], str) -> str
        raise NotImplementedError()

    @abstractmethod
    def change_service_tip(self, pos_id, table_id, percentage=None, amount=None):
        # type: (Union[int, str], str, Optional[str], Optional[str]) -> str
        raise NotImplementedError()

    @abstractmethod
    def register_service_tender(self, pos_id, table_id, tender_id, amount, orders=None, tender_details=""):
        # type: (Union[int, str], str, float, List[str], Optional[str]) -> str
        raise NotImplementedError()

    @abstractmethod
    def get_table_orders(self, pos_id, table_id):
        # type: (Union[int, str], str) -> List[Order]
        raise NotImplementedError()

    @abstractmethod
    def set_current_order(self, pos_id, order_id):
        # type: (Union[int, str], str) -> None
        raise NotImplementedError()

    @abstractmethod
    def get_service_seats_count(self, pos_id):
        # type: (Union[int, str]) -> int
        raise NotImplementedError()

    @abstractmethod
    def set_sale_line_seat(self, pos_id, seat_number, line_number, item_id, level, part_code):
        # type: (Union[int, str], int, str, str, str, str) -> None
        raise NotImplementedError()
