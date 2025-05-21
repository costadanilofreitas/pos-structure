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
from production.model import get_line_id, create_states_from_state, ProductionOrder, is_product, ProdStates
from production.model.request import ToggleTagLineRequest, ChangeProdStateRequest
from production.view import ProductionView, PrinterView, KdsView, PublishView, CommandView
from typing import List

from ._ProductionBox import ProductionBox


class OrderNotFound(Exception):
    def __init__(self, order_id):
        self.message = "Order {} not found".format(order_id)


class ViewBox(ProductionBox):
    def __init__(self, name, command_processor, order_changer, view, tag_from="TOTALED", prod_state_from="TOTALED",
                 logger=None):
        # type: (str, ProductionCommandProcessor, OrderChanger, ProductionView, str, str, Logger) -> None

        super(ViewBox, self).__init__(name, None, logger)
        self.command_processor = command_processor
        self.order_changer = order_changer
        self.view = view
        self.can_tag_states = convert_to_dict(create_states_from_state(tag_from))
        self.can_change_prod_state_states = convert_to_dict(create_states_from_state(prod_state_from))

        self._reload_view()

    def order_modified(self, order):
        if self._should_ignore_order(order):
            return

        if isinstance(self.view, KdsView):
            self._handle_kds_view(order)

        if isinstance(self.view, PublishView):
            self._handle_publish_view(order)

        if isinstance(self.view, PrinterView):
            self._handle_printer_view(order)

        if isinstance(self.view, CommandView):
            self._handle_command_view(order)

    def _handle_kds_view(self, order):
        self.save_order(order) if not order.purged else self.delete_order(order.order_id)
        self.debug("Sending order {0} to KDSView: {1}, order:\n{2}", order.order_id, self.view.name, order)
        self.view.handle_order(order)

    def _handle_publish_view(self, order):
        self.debug("Sending order {0} to Publish: {1}", order.order_id, self.view.name)
        self.view.handle_order(order)
        self._tag_order(order)

    def _handle_printer_view(self, order):
        self.debug("Sending order {0} to Printer: {1}", order.order_id, self.view.name)
        self.view.handle_order(order)
        self._tag_order(order)

    def _handle_command_view(self, order):
        self.debug("Sending Command to order: {}".format(order.order_id))
        self.view.handle_order(order)
        self._tag_order(order)

    def _tag_order(self, order):
        tags = self.view.get_view_tags()
        line_ids = self.get_order_line_ids(order)
        if len(line_ids) > 0 and len(tags) > 0:
            def tag_lines(order_to_change):
                for tag in tags:
                    for line_id in line_ids:
                        order_to_change.add_tag(line_id, tag)
                return True

            self.order_changer.change_order(order.order_id, tag_lines)

    def _should_ignore_order(self, order):
        # type: (ProductionOrder) -> bool
        stored_order = self.get_order(order.order_id)
        order_is_invalid = order.prod_state == ProdStates.INVALID
        stored_order_is_invalid = not stored_order or stored_order.prod_state == ProdStates.INVALID
        if order_is_invalid and stored_order_is_invalid:
            return True

        return order == stored_order

    def handle_view_command(self, command):
        if command.type == CommandType.toggle_tag_line:
            self._handle_add_tag_line(command)

        elif command.type == CommandType.change_prod_state:
            self._handle_change_prod_state(command)

        elif command.type == CommandType.undo:
            self.command_processor.handle_command(UndoProductionCommand(self.get_view_name()))

        elif command.type == CommandType.refresh_view:
            self._handle_refresh_view()

    def _get_order_with_exception(self, command):
        order = self.get_order(command.data.order_id)
        if not order:
            self.debug("Order {} does not exist. Reloading view...".format(command.data.order_id))
            self._reload_view()
            raise OrderNotFound(command.data.order_id)
        return order

    def _handle_add_tag_line(self, command):
        try:
            order = self._get_order_with_exception(command)
        except OrderNotFound:
            return

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

    def _handle_change_prod_state(self, command):
        try:
            order = self._get_order_with_exception(command)
        except OrderNotFound:
            return

        if not self.can_change_prod_state(order):
            self.debug("Cannot change prod state, order state {}".format(order.state))
            return

        request = command.data  # type: ChangeProdStateRequest
        if request.state in ("ITEMS_DONE", "ITEMS_SERVED"):
            order = self.get_order(request.order_id)
            line_ids = self.get_order_line_ids(order)

            tag_name = self.get_tag_by_state(request.state)
            production_command = AddTagLinesCommand(request.order_id, self.get_view_name(), line_ids, tag_name)

            debug_message = "ViewBox {} tagging with {} lines: {} from order:\n{}"
            self.debug(debug_message.format(self.name, tag_name, line_ids, str(order)))
            self.command_processor.handle_command(production_command)

        elif request.state in ("READY", "SERVED", "DELIVERED", "INVALID"):
            production_command = ChangeProdStateCommand(request.order_id, self.get_view_name(), request.state)
            self.command_processor.handle_command(production_command)

    def _handle_refresh_view(self):
        threads = []
        for order in filter(lambda x: x.prod_state != ProdStates.INVALID, self.orders.values()):
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

    @staticmethod
    def get_tag_by_state(state):
        if state == "ITEMS_DONE":
            return "done"
        elif state == "ITEMS_SERVED":
            return "served"
        return ""

    def get_order_line_ids(self, order):
        # type: (ProductionOrder) -> List[str]
        line_ids = []
        items = []
        for item in order.items:
            items.extend(item.joined_items)

        items.extend(order.items)

        for item in items:
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

    def _reload_view(self):
        if isinstance(self.view, KdsView):
            self.view.reload_handler()
