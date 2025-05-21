from ._Order import Order


class OrderFormatter(object):
    def format(self, order):
        # type: (Order) -> str
        return ";".join(
            [str(order.order_id), str(order.state_id), str(order.total_gross), str(order.total_net), str(order.discount_amount), str(order.tip)])
