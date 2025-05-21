from logging import Logger

from mw_helper import convert_to_dict
from production.command import \
    CommandType, \
    ProductionCommandProcessor, \
    ToggleTagLinesCommand, \
    ChangeProdStateCommand, \
    UndoProductionCommand, \
    AddTagLinesCommand
from production.manager import OrderChanger
from production.model import get_line_id, create_states_from_state, ProductionOrder, is_product
from production.model.request import ToggleTagLineRequest, ChangeProdStateRequest
from production.view import ProductionView, PrinterView, KdsView, PublishView
from typing import List

from ._ProductionBox import ProductionBox


class ViewBox(ProductionBox):
    def __init__(self, name, command_processor, order_changer, view, tag_from="TOTALED", prod_state_from="TOTALED", logger=None):
        # type: (str, ProductionCommandProcessor, OrderChanger, ProductionView, str, str, Logger) -> None
        super(ViewBox, self).__init__(name, None, logger)
        self.command_processor = command_processor
        self.order_changer = order_changer
        self.view = view
        self.can_tag_states = convert_to_dict(create_states_from_state(tag_from))
        self.can_change_prod_state_states = convert_to_dict(create_states_from_state(prod_state_from))

    def order_modified(self, order):
        self.save_order(order)

        if isinstance(self.view, KdsView):
            self.debug("Sending order {0} to KDS: {1}", order.order_id, self.view.name)
            self.view.handle_order(order)
        if isinstance(self.view, PublishView):
            if len(order.items) == 0:
                return

            self.debug("Sending order {0} to: {1}", order.order_id, self.view.name)
            self.view.handle_order(order)
        if isinstance(self.view, PrinterView):
            if len(order.items) == 0:
                return

            self.view.handle_order(order)
            tags = self.view.get_tags_on_print()
            line_ids = self.get_order_line_ids(order)
            if len(line_ids) > 0 and len(tags) > 0:
                def tag_lines(order_to_change):
                    for tag in tags:
                        for line_id in line_ids:
                            order_to_change.add_tag(line_id, tag)

                    return True

                self.order_changer.change_order(order.order_id, tag_lines)

    def handle_view_command(self, command):
        if command.type == CommandType.toggle_tag_line:
            order = self.get_order(command.data.order_id)
            if not self.can_tag(order):
                self.debug("Cannot tag line, order state {}".format(order.state))
                return

            request = command.data  # type: ToggleTagLineRequest

            lines = []
            for sale_line in request.lines:
                for item in order.items:
                    if int(sale_line.line_number) != int(item.line_number):
                        continue
                        
                    sale_line_key = sale_line.item_id + '.' + sale_line.part_code
                    if item.item_code == sale_line_key:
                        lines.append(get_line_id(item))
                        for joined_item in item.joined_items:
                            lines.append(get_line_id(joined_item))

            production_command = ToggleTagLinesCommand(request.order_id, self.get_view_name(), lines, request.tag_name)
            self.command_processor.handle_command(production_command)

        elif command.type == CommandType.change_prod_state:
            order = self.get_order(command.data.order_id)
            if not self.can_change_prod_state(order):
                self.debug("Cannot change prod state, order state {}".format(order.state))
                return

            request = command.data  # type: ChangeProdStateRequest
            if request.state in ("ITEMS_DONE", "ITEMS_SERVED"):
                order = self.get_order(request.order_id)
                line_ids = self.get_order_line_ids(order)

                production_command = AddTagLinesCommand(request.order_id,
                                                        self.get_view_name(),
                                                        line_ids,
                                                        self.get_tag_by_state(request.state))
                self.debug("ViewBox {} tagging with {} lines: {} from order:\n{}"
                           .format(self.name,
                                   production_command.tag,
                                   line_ids,
                                   str(order)))
                self.command_processor.handle_command(production_command)
            elif request.state in ("READY", "SERVED", "DELIVERED", "INVALID"):
                production_command = ChangeProdStateCommand(request.order_id, self.get_view_name(), request.state)
                self.command_processor.handle_command(production_command)

        elif command.type == CommandType.undo:
            self.command_processor.handle_command(UndoProductionCommand(self.get_view_name()))

        elif command.type == CommandType.refresh_view:
            threads = []
            for order in self.orders.values():
                threads.append(self.view.handle_order(order))

            for thread in threads:
                thread.join()

            if isinstance(self.view, KdsView):
                self.view.refresh_end()

    def can_tag(self, order):
        return order.state in self.can_tag_states

    def can_change_prod_state(self, order):
        return order.state in self.can_change_prod_state_states

    def get_view_name(self):
        if isinstance(self.view, KdsView):
            return self.view.view_name
        return None

    def get_tag_by_state(self, state):
        if state == "ITEMS_DONE":
            return "done"
        elif state == "ITEMS_SERVED":
            return "served"
        return ""

    def get_order_line_ids(self, order):
        # type: (ProductionOrder) -> List[str]
        line_ids = []
        for item in order.items:
            self.get_item_line_ids(item, line_ids)

        return line_ids

    def get_item_line_ids(self, item, line_ids):
        if is_product(item):
            line_ids.append(get_line_id(item))
            for joined_item in item.joined_items:
                line_ids.append(get_line_id(joined_item))
        else:
            for son in item.items:
                self.get_item_line_ids(son, line_ids)
