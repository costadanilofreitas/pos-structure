from application.domain import TableService, OrderManager  # noqa
from application.domain.ui import ScreenChanger, ScreenIdEnum  # noqa

ACK_RESPONSE = "0"


class CreateTableOrderInteractor(object):

    def __init__(self, table_service, screen_changer, order_manager):
        # type: (TableService, ScreenChanger, OrderManager) -> None
        self.table_service = table_service
        self.screen_changer = screen_changer
        self.order_manager = order_manager

    def execute(self, pos_id, table_id, pricelist):
        # type: (str, str) -> str

        current_order_state = self.order_manager.get_current_order_state(pos_id)
        if current_order_state == "IN_PROGRESS":
            self.order_manager.store_order(pos_id)
        self.table_service.create_order(pos_id, table_id, pricelist)

        return ACK_RESPONSE
