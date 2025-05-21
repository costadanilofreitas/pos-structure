import logging
from production.command import ChangePathCommand
from production.model import ProdStates, ProductionOrder
from typing import Dict, List

from ._ProductionBox import ProductionBox


class NoAvailablePaths(Exception):
    pass


class OrderRoundRobinBox(ProductionBox):
    def __init__(self, name, sons, order_changer, paths, logger=None):
        super(OrderRoundRobinBox, self).__init__(name, sons, logger)
        self.order_changer = order_changer
        self.paths = paths
        self.paths_dict = {}  # type: Dict[str, OrderRoundRobinBox.Path]
        self.lowest_height_priority = []  # type: List[str]

        index = 0
        for path in paths:
            self.paths_dict[path] = OrderRoundRobinBox.Path(path, index, sons[index])
            self.lowest_height_priority.append(path)
            index += 1

        self.order_path = {}  # type: Dict[int, OrderRoundRobinBox.Path]
        self.stored_orders = []

    def order_modified(self, order):
        self.logger.debug("Box name: {} - Routing order:\n{}\n".format(self.name, order))
        if order.round_robin_path or order.order_id in self.order_path:
            self.logger.debug("Order previously routed")
            if order.order_id in self.order_path:
                current_path_name = self.order_path[order.order_id].name
            else:
                current_path_name = order.round_robin_path

            current_path = self.paths_dict[current_path_name]
            if order.order_id in self.order_path:
                if order.prod_state in (ProdStates.SERVED, ProdStates.INVALID):
                    self.logger.debug("Know SERVED order, removing from internal dictionaries")
                    del self.order_path[order.order_id]
                    current_path.height -= self._get_order_points(current_path.orders[order.order_id])
                    del current_path.orders[order.order_id]
                else:
                    self.logger.debug("Know not SERVED order, updating internal dictionaries")
                    current_path.height -= self._get_order_points(current_path.orders[order.order_id])
                    current_path.height += self._get_order_points(order)
                    current_path.orders[order.order_id] = order
            elif order.prod_state != ProdStates.SERVED:
                self.logger.debug("Unknown not SERVED order, adding to internal dictionaries")
                current_path.height += self._get_order_points(order)
                self.order_path[order.order_id] = current_path
                current_path.orders[order.order_id] = order

            self.publish_order(current_path_name, order)
        else:
            self.logger.debug("Order never routed")
            if self.refreshing:
                self.logger.debug("Refreshing views. Storing order to process later")
                self.stored_orders.append(order)
                return

            if order.prod_state not in (ProdStates.SERVED, ProdStates.INVALID):
                self.logger.debug("Not served order, adding to internal dictionaries")
                try:
                    lowest_height_path = self.get_lowest_height_path()
                    lowest_height_path.orders[order.order_id] = order
                    lowest_height_path.height += self._get_order_points(order)

                    self.add_path_to_root_order(order, lowest_height_path.name)
                    self.order_path[order.order_id] = lowest_height_path
                    self.publish_order(lowest_height_path.name, order)

                except NoAvailablePaths:
                    self.logger.debug("No available paths")
                    order.prod_state = ProdStates.INVALID
                    self.publish_order_to_all_sons(order)
                    return

            else:
                self.logger.debug("Served order, just propagating to sons")
                self.publish_order_to_all_sons(order)

        if self.logger.level >= logging.DEBUG:
            paths = "Paths and priorities:\n"
            for path in self.paths:
                paths += str(self.paths_dict[path]) + "\n"
            for value in self.lowest_height_priority:
                paths += str(value) + "\n"
            self.logger.debug(paths)

    @staticmethod
    def _get_order_points(order):
        return order.points or 0

    @staticmethod
    def remove_round_robin_path(root_order):
        del root_order.round_robin_path
        return True

    def handle_production_command(self, command):
        if not isinstance(command, ChangePathCommand):
            return super(OrderRoundRobinBox, self).handle_production_command(command)

        order_handled = False
        if command.path in self.paths_dict and self.paths_dict[command.path].enabled != command.enabled:
            self.logger.debug("Changing enable state of path {} to {}".format(command.path, command.enabled))
            order_handled = True
            self.paths_dict[command.path].enabled = command.enabled
            if not command.enabled:
                for order in self.paths_dict[command.path].get_order_list():
                    self.order_changer.change_order(order.order_id, self.remove_round_robin_path)

        super(OrderRoundRobinBox, self).handle_production_command(command)
        return order_handled

    def start_refresh(self):
        self.logger.debug("{} - Start Refresh".format(self.name))

        super(OrderRoundRobinBox, self).start_refresh()
        self.order_path.clear()
        for path in self.paths_dict.values():
            path.height = 0
            path.clear_orders()

    def end_refresh(self):
        self.logger.debug("{} - End Refresh".format(self.name))

        super(OrderRoundRobinBox, self).end_refresh()
        for order in self.stored_orders:
            self.order_modified(order)
        self.stored_orders = []

    def __setattr__(self, name, value):
        if name == "sons" and isinstance(value, list):
            if hasattr(self, "paths_dict"):
                for path in self.paths_dict.values():
                    path.son = value[path.index]
            super(OrderRoundRobinBox, self).__setattr__(name, value)
        else:
            super(OrderRoundRobinBox, self).__setattr__(name, value)

    def get_lowest_height_path(self):
        lowest_height_paths = self.get_lowest_height_paths()
        highest_priority_index = min(map(lambda x: self.lowest_height_priority.index(x.name), lowest_height_paths))
        highest_priority_path = self.lowest_height_priority.pop(highest_priority_index)
        self.lowest_height_priority.append(highest_priority_path)
        return self.paths_dict[highest_priority_path]

    def get_lowest_height_paths(self):
        lowest = None
        for path in self.paths_dict.values():
            if path.enabled and (lowest is None or path.height < lowest):
                lowest = path.height

        ret = []
        for path in self.paths_dict.values():
            if path.enabled and path.height == lowest:
                ret.append(path)

        if not ret:
            raise NoAvailablePaths()
        return ret

    def publish_order(self, lowest_height_path, order):
        # type: (str, ProductionOrder) -> None

        invalid_order = order.clone()
        invalid_order.prod_state = ProdStates.INVALID
        if hasattr(invalid_order, "stamped"):
            del invalid_order.stamped

        for path in self.paths_dict.values():
            if path.name == lowest_height_path:
                path.son.order_modified(order)
            else:
                path.son.order_modified(invalid_order)

    def publish_order_to_all_sons(self, order):
        for son in self.sons:
            son.order_modified(order)

    def add_path_to_root_order(self, order, path):
        def change_order(root_order):
            root_order.round_robin_path = path
            return True

        self.order_changer.change_order(order.order_id, change_order)

    class Path(object):
        def __init__(self, name, index, son):
            self.name = name
            self.index = index
            self.son = son
            self.enabled = True
            self.height = 0
            self.orders = {}

        def get_order_list(self):
            return list(self.orders.values())

        def clear_orders(self):
            self.orders = {}

        def __str__(self):
            return "{}: {{Height: {}, Enabled: {}, Order Counts: {}}}".format(self.name,
                                                                              self.height,
                                                                              self.enabled,
                                                                              len(self.orders))

        def __repr__(self):
            return self.__str__()
