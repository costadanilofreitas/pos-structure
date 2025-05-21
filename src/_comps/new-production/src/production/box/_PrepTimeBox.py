from datetime import datetime, timedelta
from logging import Logger

from production.box import ProductionBox
from production.box._OrderChangerProductionBox import OrderChangerProductionBox
from production.model import Item
from timeutil import Clock
from typing import List, Dict, Union, Any


class PrepTree(object):
    def __init__(self, item):
        self.item = item
        self.sons = []  # type: List[PrepTree]
        self.parents = []  # type: List[PrepTree]


class PrepTimeBox(OrderChangerProductionBox):

    def __init__(self, name, sons, prep_times, clock, publish_scheduler=None, wait_even_if_done=False, logger=None):
        # type: (str, Union[ProductionBox, List[ProductionBox]], Dict[int, int], Clock, Any, bool, Logger) -> None
        super(PrepTimeBox, self).__init__(name, sons, logger)
        self.prep_times = prep_times
        self.clock = clock
        self.publish_scheduler = publish_scheduler
        self.wait_even_if_done = wait_even_if_done

    def change_order(self, order):
        order_send_moment = self.add_prep_time_and_default_send_moment(order)

        lines = self.get_lines_with_items_ordered_by_prep_time(order.items)
        if len(lines) == 0:
            return order

        order.max_prep_time = lines[0][0].prep_time
        now = self.clock.now()
        publish_times = []
        already_processed = self.add_send_moment_on_items(lines, now, order_send_moment, publish_times)
        self.handle_rebel_items(already_processed, lines, now, publish_times)
        if self.publish_scheduler and len(publish_times) > 0:
            publish_time = min(publish_times)
            self.debug("Scheduling publish in {} seconds".format(publish_time))
            self.publish_scheduler.schedule_publish(order.order_id, publish_time)
        else:
            self.debug("Not publishing")

        return order

    def add_send_moment_on_items(self, lines, now, order_send_moment, publish_times):
        already_processed = {}
        item_with_max_level = None
        highest_item, highest_line = self.get_highest_level_item(lines, already_processed)
        while highest_item is not None:
            if self.item_has_max_prep_time(item_with_max_level, highest_item):
                if item_with_max_level is not None:
                    highest_item.send_moment = item_with_max_level.send_moment
                else:
                    highest_item.send_moment = order_send_moment
                self.set_current_level(highest_item, now)
            else:
                if item_with_max_level.current_level <= highest_item.current_level:
                    highest_item.send_moment = self.get_send_moment(highest_item, item_with_max_level)
                    self.set_current_level(highest_item, now)
                else:
                    activate_time = self.get_doing_time(item_with_max_level)
                    if activate_time is not None:
                        highest_item.send_moment = self.get_send_moment(highest_item, item_with_max_level)
                        if int((highest_item.send_moment - now).total_seconds()) > 0:
                            publish_times.append(int((highest_item.send_moment - now).total_seconds()))
                            highest_item.add_tag("wait-prep-time")

            if self.is_item_the_highest(highest_item, item_with_max_level):
                item_with_max_level = highest_item
            already_processed[highest_item] = highest_item
            self.handle_line(highest_line, highest_item, now, already_processed, publish_times)
            highest_item, highest_line = self.get_highest_level_item(lines, already_processed)
        return already_processed

    def item_has_max_prep_time(self, previous_item, highest_item):
        return previous_item is None or previous_item.prep_time == highest_item.prep_time

    def is_item_the_highest(self, current_item, item_with_max_level):
        if item_with_max_level is None or \
                (item_with_max_level.prep_time == current_item.prep_time and
                 current_item.current_level > item_with_max_level.current_level):
            return True

        if current_item.current_level == item_with_max_level.current_level:
            if "done" in current_item.tags and "done" in item_with_max_level.tags:
                if self.get_done_time(current_item) > self.get_done_time(item_with_max_level):
                    return True

        return False

    def handle_rebel_items(self, already_processed, lines, now, publish_times):
        for line in lines:
            first = True
            for item in line:
                if item.send_moment is None and ("done" in item.tags or "doing" in item.tags):
                    item.send_moment = self.get_send_moment(item, None)
                    if first:
                        self.handle_line(line, item, now, already_processed, publish_times)
                        first = False

                if item.send_moment is None or int((item.send_moment - now).total_seconds()) > 0:
                    item.add_tag("wait-prep-time")

    def add_prep_time_and_default_send_moment(self, order):
        for item in order.items:
            self._calculate_item_prep_time(item)

        if order.display_time:
            order_send_moment = datetime.strptime(order.display_time, "%Y-%m-%dT%H:%M:%S.%f")
        else:
            order_send_moment = datetime.strptime(order.created_at, "%Y-%m-%dT%H:%M:%S.%f")
        self.add_default_send_moment(order.items, order_send_moment)

        return order_send_moment

    def set_current_level(self, highest_item, now):
        if "done" in highest_item.tags:
            highest_item.current_level = 0
        elif "doing" in highest_item.tags:
            activate_time = self.get_last_tag_date(highest_item, "doing")
            elapsed_time = int((now - activate_time).total_seconds())
            highest_item.current_level = highest_item.prep_time - elapsed_time

    def get_highest_level_item(self, lines, already_processed):
        highest_line = None
        highest_item = None
        for line in lines:
            for item in line:
                if item not in already_processed and\
                        (highest_item is None or item.current_level > highest_item.current_level):
                    highest_item = item
                    highest_line = line

        return highest_item, highest_line

    def add_default_send_moment(self, items, send_moment):
        for item in items:
            if item.is_product():
                if item.qty == 0:
                    item.send_moment = None
                elif item.prep_time == -1:
                    item.send_moment = send_moment
            else:
                self.add_default_send_moment(item.items, send_moment)

    def handle_line(self, line, highest_prep, now, already_processed, publish_times):
        for item in line:
            if highest_prep.send_moment is None or \
                    item.send_moment is not None or \
                    "done" in item.tags or \
                    "doing" in item.tags:
                continue

            item.send_moment = self.get_send_moment(item, highest_prep)
            if item.send_moment is not None and int((item.send_moment - now).total_seconds()) > 0:
                item.add_tag("wait-prep-time")
                publish_times.append(int((item.send_moment - now).total_seconds()))
            else:
                item.remove_tag("wait-prep-time")
            already_processed[item] = item

    def get_doing_time(self, item):
        if "doing" in item.tags:
            return self.get_last_tag_date(item, "doing")
        else:
            return None

    def get_done_time(self, item):
        if "done" in item.tags:
            return self.get_last_tag_date(item, "done")
        else:
            return None

    def get_send_moment(self, current_item, item_with_max_level):
        possible_send_moments = []
        if item_with_max_level is not None and "done" in item_with_max_level.tags:
            possible_send_moments.append(self.get_done_time(item_with_max_level))

        if item_with_max_level is not None and "doing" in item_with_max_level.tags:
            prep_delta = item_with_max_level.prep_time - current_item.prep_time
            send_moment = self.get_doing_time(item_with_max_level) + timedelta(seconds=prep_delta)
            possible_send_moments.append(send_moment)

        if "doing" in current_item.tags:
            possible_send_moments.append(self.get_doing_time(current_item))

        if "done" in current_item.tags:
            possible_send_moments.append(self.get_done_time(current_item))

        if len(possible_send_moments) == 0:
            return None

        return min(possible_send_moments)

    def get_last_doing(self, parents):
        return self.get_last_with_tag(parents, "doing")

    def get_last_done(self, parents):
        return self.get_last_with_tag(parents, "done")

    def get_last_with_tag(self, parents, tag):
        tag_dates = []
        for parent in parents:
            tag_date = self.get_last_tag_date(parent.item, tag)
            if tag_date is not None:
                tag_dates.append(tag_date)
        if len(tag_dates) > 0:
            return max(tag_dates)
        return None

    def get_last_tag_date(self, item, tag):
        for event in reversed(item.tag_history):
            if event.tag == tag:
                return event.date
        return None

    def _calculate_item_prep_time(self, item, fire=False):
        if item.is_product():
            if fire:
                item.fire = True

            item.prep_time = self.get_product_prep_time(item)
            item.current_level = item.prep_time
        else:
            for son in item.items:
                is_fire = True if fire else "fire" in item.properties
                self._calculate_item_prep_time(son, is_fire)

    def get_product_prep_time(self, item):
        # type: (Item) -> int
        if "fire" in item.properties or item.qty == 0:
            return -1

        prep_time = 0
        has_prep_time = False
        if item.part_code in self.prep_times:
            prep_time = self.prep_times[item.part_code]
            has_prep_time = True
        for son in item.items:
            son_prep_time = self.get_product_prep_time(son)
            if son_prep_time != -1:
                prep_time += son_prep_time
                has_prep_time = True

        if has_prep_time:
            return prep_time
        else:
            return -1

    def get_lines_with_items_ordered_by_prep_time(self, order_items):
        lines = []
        for order_item in order_items:
            item_with_prep_time = self._get_order_products_with_prep_time([order_item])
            if not item_with_prep_time:
                continue
            lines.append(item_with_prep_time)
        return lines

    def _get_order_products_with_prep_time(self, items):
        order_products = []
        for item in items:
            if item.is_product() and item.prep_time and item.prep_time > 0:
                order_products.append(item)
            elif not item.is_product():
                order_products.extend(self._get_order_products_with_prep_time(item.items))

        return order_products
