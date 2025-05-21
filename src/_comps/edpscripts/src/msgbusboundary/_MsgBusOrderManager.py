from application.domain import OrderManager, SaleLine  # noqa
from sysactions import get_posot, get_model


class MsgBusOrderManager(OrderManager):

    def recall_order(self, pos_id, order_id):
        model = get_model(pos_id)
        pos_ot = get_posot(model)
        pos_ot.recallOrder(pos_id, order_id)

    def store_order(self, pos_id):
        model = get_model(pos_id)
        pos_ot = get_posot(model)
        pos_ot.storeOrder(pos_id)

    def change_line_seat(self, pos_id, sale_line, seat_number):
        # type: (str, SaleLine, str) -> None

        model = get_model(pos_id)
        pos_ot = get_posot(model)

        pos_ot.setOrderCustomProperty("seat",
                                      str(seat_number),
                                      sale_line.order_id,
                                      sale_line.line_number,
                                      sale_line.item_id,
                                      sale_line.level,
                                      sale_line.part_code)

    def get_current_order_state(self, pos_id):
        model = get_model(pos_id)

        order_node = model.find("CurrentOrder/Order")
        if order_node is not None:
            return order_node.get("state")
        return None
