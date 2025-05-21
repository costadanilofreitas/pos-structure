from . import StatisticBox


class TimePercentageStatisticBox(StatisticBox):
    def __init__(self, name, sons, statistic_updater, logger, get_config):
        super(TimePercentageStatisticBox, self).__init__(name, sons, statistic_updater, logger, get_config)
        self.mode = get_config("Mode")
        self.threshold = int(get_config("Threshold"))
        self.tag = get_config("TagName")
        self.all_tagged_orders = []
        self.orders_in_threshold = []

    def update_statistics(self, order):
        order_id = order.order_id

        try:
            self.all_tagged_orders.remove(order_id)
            self.orders_in_threshold.remove(order_id)
        except ValueError:
            pass

        if self.tag in order.tags:
            self.all_tagged_orders.append(order_id)

            tag_time = int(order.tags[self.tag])

            if self.is_over_threshold(tag_time) or self.is_under_threshold(tag_time):
                self.debug("Order {} {} {} seconds".format(order_id, self.mode, self.threshold))
                self.orders_in_threshold.append(order_id)

            return self.get_time_percentage(len(self.orders_in_threshold))

    def is_under_threshold(self, tag_time):
        return self.mode == "UNDER" and tag_time < self.threshold

    def is_over_threshold(self, tag_time):
        return self.mode == "OVER" and tag_time > self.threshold

    def get_time_percentage(self, tagged_count):
        total = len(self.all_tagged_orders) or 1
        return "{:.2f}".format(100 * (float(tagged_count) / total))
