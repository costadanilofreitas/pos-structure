from logging import Logger

from production.box import ProductionBox
from production.command import ChangePathCommand
from production.model import ProductionOrder, ProdStates
from typing import List, Tuple


class DistributorBox(ProductionBox):
    def __init__(self, name, paths, logger=None):
        # type: (str, List[Tuple[str, ProductionBox]], Logger) -> None
        self.path_box = {}
        self.paths = []
        self.paths_dict = {}
        self.active_path = None
        self.old_active = None

        sons = []
        index = 0
        for path in paths:
            if self.active_path is None:
                self.active_path = path

            path_obj = Path(path, index, True)

            self.paths.append(path_obj)
            self.paths_dict[path] = path_obj

            self.path_box[path] = index
            index += 1

        super(DistributorBox, self).__init__(name, sons, logger)

    def end_refresh(self):
        self.old_active = None
        super(DistributorBox, self).end_refresh()

    def order_modified(self, order):
        if self.old_active is not None:
            invalid_order = order.clone()
            invalid_order.prod_state = ProdStates.INVALID
            if hasattr(order, "stamped"):
                del invalid_order.stamped
            self.debug("DistributorBox {}: Invalidating order {} on path {}", self.name, order.order_id, self.old_active)
            self.sons[self.paths_dict[self.old_active].son_index].order_modified(invalid_order)
        if self.active_path is not None:
            self.debug("DistributorBox {}: Sending to {}", self.name, self.active_path)
            self.sons[self.paths_dict[self.active_path].son_index].order_modified(order)
        else:
            self.debug("DistributorBox {}: No active path.", self.name)

    def handle_production_command(self, command):
        if not isinstance(command, ChangePathCommand):
            return False

        result = False
        if command.path in self.paths_dict and self.paths_dict[command.path].enabled != command.enabled:
            self.paths_dict[command.path].enabled = command.enabled
            result = True

            self.old_active = self.active_path
            self.active_path = None
            for path in self.paths:
                if path.enabled:
                    self.active_path = path.name
                    break
            if self.active_path == self.old_active:
                self.old_active = None

        super(DistributorBox, self).handle_production_command(command)
        return result


class Path(object):
    def __init__(self, name, son_index, enabled):
        self.name = name
        self.son_index = son_index
        self.enabled = enabled
