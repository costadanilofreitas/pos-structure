from . import StatisticBox


def format_seconds(seconds):
    # type: (float) -> str
    only_seconds = int(seconds % 60)
    only_minutes = int((seconds / 60) % 60)
    only_hours = int(seconds / 3600)
    return '{:02d}:{:02d}:{:02d}'.format(only_hours, only_minutes, only_seconds)


class MeanTimeStatisticBox(StatisticBox):
    def __init__(self, name, sons, statistic_updater, logger, get_config):
        super(MeanTimeStatisticBox, self).__init__(name, sons, statistic_updater, logger, get_config)
        self.statistics = {}
        self.tag = get_config("TagName")

    def update_statistics(self, order):
        order_id = order.order_id

        self.debug('Got order! Order: {}', order)

        if self.tag not in order.tags:
            if order_id in self.statistics:
                del self.statistics[order_id]
        else:
            self.statistics[order_id] = order.tags[self.tag]
            self.debug('added order to statistics')
            service_mean_time = sum(self.statistics.itervalues()) / (len(self.statistics) or 1)
            return format_seconds(service_mean_time)
