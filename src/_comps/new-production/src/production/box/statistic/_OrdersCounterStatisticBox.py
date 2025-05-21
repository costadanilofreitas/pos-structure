from . import StatisticBox


class OrdersCounterStatisticBox(StatisticBox):
    def __init__(self, name, sons, statistic_updater, logger, get_config):
        super(OrdersCounterStatisticBox, self).__init__(name, sons, statistic_updater, logger, get_config)
        self.orders = []

    def update_statistics(self, order):
        order_id = order.order_id
        if order_id not in self.orders:
            self.orders.append(order_id)

        return len(self.orders)
