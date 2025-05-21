from common import state_match, check_and_remove
from . import StatisticBox


class ReadingPercentageStatisticBox(StatisticBox):
    def __init__(self, name, sons, statistic_updater, logger, get_config):
        super(ReadingPercentageStatisticBox, self).__init__(name, sons, statistic_updater, logger, get_config)
        self.orders = []
        self.orders_matched = []
        self.state_value = get_config("State").get("Value")
        self.state_type = get_config("State").get("Type")

    def update_statistics(self, order):
        order_id = order.order_id
        if order_id not in self.orders:
            self.orders.append(order_id)

        check_and_remove(self.orders, order, self.state_type, self.state_value, False)
        check_and_remove(self.orders_matched, order, self.state_type, self.state_value)

        if order_id not in self.orders_matched and state_match(order, self.state_type, self.state_value):
            self.orders_matched.append(order_id)

        return "{:.2f}".format((100 * (float(len(self.orders_matched)) / (len(self.orders) or 1))))
