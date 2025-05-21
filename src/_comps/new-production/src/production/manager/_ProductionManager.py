import json
import time
from datetime import datetime, timedelta
from logging import Logger
from threading import Lock, Condition, Thread, local

from mw_helper import ensure_list
from production.box import ProductionBox
from production.command import ProductionCommandProcessor, ToggleTagLinesCommand, ChangeProdStateCommand, \
    UndoProductionCommand, AddTagLinesCommand, ChangePathCommand, OrderModifiedCommand, PublishOrderCommand, \
    ProductionCommand, PurgeOrdersCommand
from production.command.undo import UndoCommand, TagLinesUndoCommand, ChangeProdStateUndoCommand, \
    TagLinesUndoCommandType
from production.model import ProductionOrder, ProdStates
from production.repository import ProductionRepository
from production.view import OrderXml
from messagebus import MessageBus, Message, DataType, TokenPriority, TokenCreator
from typing import List, Dict, Any

from ._CommandQueue import CommandQueue
from ._OrderChanger import OrderChanger
from ._PublishScheduler import PublishScheduler
from ._StatisticUpdater import StatisticUpdater


MSGGRP_KDS = '0B'
TK_KDS_UPDATE_STATISTICS = TokenCreator.create_token(TokenPriority.high, MSGGRP_KDS, "21")


class ProductionManager(ProductionCommandProcessor, PublishScheduler, OrderChanger, StatisticUpdater):
    def __init__(self, production_repository, purge_interval, orders_life_time, message_bus, logger):
        # type: (ProductionRepository, int, int, MessageBus, Logger) -> None
        self.production_repository = production_repository
        self.purge_interval = purge_interval
        self.orders_life_time = orders_life_time
        self.message_bus = message_bus
        self.logger = logger

        self.boxes = []  # type: List[ProductionBox]
        self.orders = {}  # type: Dict[int, ProductionOrder]
        self.undo_lock = Lock()
        self.undo_view_map = {}  # type: Dict[str, List[UndoCommand]]
        self.waiters = {}  # type: Dict[int, ProductionManager.PublishWaiter]
        self.waiter_lock = Lock()
        self.purge_waiter = None  # type: ProductionManager.PurgeWaiter
        self.statistics = {}  # type: Dict[str, Any]
        self.statistics_changed = local()
        self.statistics_changed.value = None

        self.command_queue = CommandQueue(self, self.logger)

    def remove_tags(self, items):
        for item in items:
            item.tags = {}
            item.tag_history = []

            self.remove_tags(item.items)

    def initialize(self):
        self.purge_waiter = ProductionManager.PurgeWaiter(self, self.logger)
        self.purge_waiter.purge_orders()
        self._wait_purging_orders()
        
        for order in self.production_repository.get_all_orders():
            order.first_processing = False
            for undo_command in order.undo_list:  # type: UndoCommand
                self.enqueue_undo_command(undo_command.view, undo_command)
            self.orders[order.order_id] = order
            self.sync_publish_order(order)

        self.purge_waiter.purge_orders_and_wait()
        
    def purge_all_orders(self):
        self.purge_waiter = ProductionManager.PurgeWaiter(self, self.logger)
        self.purge_waiter.purge_orders(all_orders=True)

    @staticmethod
    def _wait_purging_orders():
        time.sleep(5)

    def set_root_boxes(self, boxes):
        # type: (List[ProductionBox]) -> None
        self.boxes = boxes
        for box in self.boxes:
            box.parent = self

    def process_command(self, command):
        # type: (ProductionCommand) -> None
        order = None
        if isinstance(command, OrderModifiedCommand):
            order = command.order

            if order.order_id in self.orders:
                order.first_processing = False
                saved_order = self.orders[order.order_id]
                order.prod_state = saved_order.prod_state
                self.update_order_items(order, saved_order)
                if hasattr(saved_order, "round_robin_path"):
                    order.round_robin_path = saved_order.round_robin_path
            else:
                order.first_processing = True

            self.statistics_changed.value = False
            self.orders[order.order_id] = order
            self.production_repository.save_order(order)
            self.sync_publish_order(order)
            self.send_statistics_update()
            return

        elif isinstance(command, PublishOrderCommand):
            self.sync_publish_order(command.order)
            return

        elif isinstance(command, PurgeOrdersCommand):
            self.logger.debug("Purging orders command start")
            self.production_repository.purge_orders(command.orders)
            cached_purged_orders = self._get_cached_purged_orders(command.orders)
            self.logger.debug("Syncing cached purged orders")
            for order in cached_purged_orders:
                self.sync_publish_order(order)
                self.orders.pop(order.order_id, None)
            return

        elif isinstance(command, ToggleTagLinesCommand) or isinstance(command, AddTagLinesCommand):
            order = self.tag_lines(command)

        elif isinstance(command, ChangeProdStateCommand):
            order = self.orders[command.order_id]

            state_undo_command = ChangeProdStateUndoCommand(order.order_id, command.view, order.prod_state, [])
            self.add_undo_command_to_order_and_view(command.view, order, state_undo_command)

            order.prod_state = command.state
            self.statistics_changed.value = False
            self.send_statistics_update()

        elif isinstance(command, UndoProductionCommand):
            view_undo_commands = self.undo_view_map[command.view]
            if len(view_undo_commands) == 0:
                return

            with self.undo_lock:
                next_available = None
                for undo_command in view_undo_commands:
                    if undo_command.is_enabled():
                        next_available = undo_command
                        break

                if next_available is not None:
                    view_undo_commands.remove(next_available)

            if next_available is None:
                return

            if next_available.order_id not in self.orders:
                self.logger.info("The order {} has no longer available".format(next_available.order_id))
                return

            order = self.orders[next_available.order_id]
            if order is None:
                return

            next_available.undo(order)

        elif isinstance(command, ChangePathCommand):
            handled = self.publish_command(command)
            for box in handled:
                box.start_refresh()
                for order in self.orders.values():
                    box.order_modified(order.clone())
                box.end_refresh()

        else:
            self.logger.error("[process_command] Unknown command received: {}".format(type(command)))

        if order is not None:
            self.production_repository.save_order(order)
            self.sync_publish_order(order)

    def order_modified(self, order):
        # type: (ProductionOrder) -> None
        self.command_queue.put(OrderModifiedCommand(order.order_id, order))

    def update_order_items(self, order, saved_order):
        # type: (ProductionOrder, ProductionOrder) -> None
        for item in order.items:
            for saved_item in saved_order.items:
                if item.get_line_id() == saved_item.get_line_id():
                    self.add_saved_tags_to_item(item, saved_item)

    def add_saved_tags_to_item(self, item, saved_item):
        item.tags = saved_item.tags
        item.tag_history = saved_item.tag_history
        for son in item.items:
            for saved_son in saved_item.items:
                if son.get_line_id() == saved_son.get_line_id():
                    self.add_saved_tags_to_item(son, saved_son)

    def handle_command(self, command):
        self.command_queue.put(command)

    def schedule_publish(self, order_id, wait_time):
        order = self.orders[order_id]
        publish_waiter = ProductionManager.PublishWaiter(self, order, wait_time)
        start_thread = False
        waiter_to_deactivate = None
        with self.waiter_lock:
            if order.order_id in self.waiters:
                if self.waiters[order.order_id].wait_time > wait_time:
                    waiter_to_deactivate = self.waiters[order.order_id]
                    del self.waiters[order.order_id]
                    self.waiters[order.order_id] = publish_waiter
                    start_thread = True
            else:
                self.waiters[order.order_id] = publish_waiter
                start_thread = True

        if waiter_to_deactivate is not None:
            waiter_to_deactivate.deactivate()

        if start_thread:
            publish_waiter.wait_and_publish()

    def change_order(self, order_id, order_changer):
        if order_id in self.orders:
            order = self.orders[order_id]
            if order_changer(order):
                self.production_repository.save_order(order)

    def change_items(self, order, item_changer):
        saved_order = self.orders[order.order_id]
        was_change = False

        def get_diff_key(x):
            return '{}-{}-{}'.format(x.line_number, x.item_id, x.part_code)

        def set_all_items(item_view, item_save, item_setter):
            if item_save.is_product():
                if get_diff_key(item_save) == get_diff_key(item_view):
                    return item_setter(item_save)
                return False
            else:
                were_change = False
                for son in item_save.items:
                    if set_all_items(item_view, son, item_setter):
                        were_change = True
                return were_change

        for view_item in order.items:
            for saved_item in saved_order.items:
                if set_all_items(view_item, saved_item, item_changer):
                    was_change = True

        if was_change:
            self.production_repository.save_order(saved_order)

    def tag_lines(self, command):
        order = self.orders[command.order_id]
        self.change_order_tags(command, order)
        self.create_undo_command(command, order)
        return order

    @staticmethod
    def change_order_tags(command, order):
        tags = ensure_list(command.tag)
        if isinstance(command, ToggleTagLinesCommand):
            for tag in tags:
                for line_id in command.line_ids:
                    order.toggle_tag(line_id, tag)
        else:
            for tag in tags:
                for line_id in command.line_ids:
                    order.add_tag(line_id, tag)

    def create_undo_command(self, command, order):
        undo_command = self.build_undo_command(command, order)
        self.add_undo_command_to_order_and_view(command.view, order, undo_command)

    def build_undo_command(self, command, order):
        disabled_commands = self.get_disabled_commands(command, order)
        if isinstance(command, ToggleTagLinesCommand):
            undo_type = TagLinesUndoCommandType.toggle
        else:
            undo_type = TagLinesUndoCommandType.add
        undo_command = TagLinesUndoCommand(order.order_id,
                                           command.view,
                                           command.tag,
                                           command.line_ids,
                                           undo_type,
                                           disabled_commands)
        return undo_command

    @staticmethod
    def get_disabled_commands(command, order):
        disabled_commands = []
        if command.tag == "served":
            for undo_command in order.undo_list:
                if isinstance(undo_command, TagLinesUndoCommand) and undo_command.tag in ("doing", "done"):
                    undo_command.disable()
                    disabled_commands.append(undo_command)
        return disabled_commands

    def get_order_xml(self, order_id):
        if order_id not in self.orders:
            return None
        return OrderXml().to_xml(self.orders[order_id])

    def get_production_order(self, order_id):
        if order_id not in self.orders:
            return None
        return self.orders[order_id]

    def publish_order(self, order):
        self.command_queue.put(PublishOrderCommand(order.order_id, order))

    def sync_publish_order(self, order):
        self.logger.info("Publishing order: {}".format(order.order_id))
        with self.waiter_lock:
            if order.order_id in self.waiters:
                self.waiters[order.order_id].deactivate()
                del self.waiters[order.order_id]

        for box in self.boxes:
            try:
                self.logger.debug("\n#region {}".format(box.name))
                box.order_modified(order.clone())
            except:
                self.logger.exception("Exception on box: {}".format(box.name))
            finally:
                self.logger.debug("\n#endregion")

        self.logger.info("Finished publishing order: {}".format(order.order_id))

    def publish_command(self, command):
        handled = []
        for box in self.boxes:
            try:
                if box.handle_production_command(command):
                    handled.append(box)
            except Exception as _:
                self.logger.exception("Exception on box: {}".format(box.name))

        return handled

    @staticmethod
    def add_tag_to_dict(tags, line_id, tag):
        if line_id not in tags:
            tags[line_id] = []
        tags[line_id].append(tag)

    def add_undo_command_to_order_and_view(self, view, order, undo_command):
        order.undo_list.append(undo_command)
        self.enqueue_undo_command(view, undo_command)

    def enqueue_undo_command(self, view, undo_command):
        with self.undo_lock:
            if view not in self.undo_view_map:
                self.undo_view_map[view] = []
            self.undo_view_map[view].insert(0, undo_command)

    def stop(self):
        if self.purge_waiter is not None:
            self.purge_waiter.deactivate()

    def _get_cached_purged_orders(self, orders_to_purge):
        # type: (List[int]) -> List[ProductionOrder]
        orders = []
        for order_id in orders_to_purge:
            if order_id in self.orders:
                order = self.orders[order_id]
                order.prod_state = ProdStates.INVALID
                order.items = []
                orders.append(order)
        return orders

    def update_statistics(self, order_id, stats):
        self.statistics_changed.value = True
        self.statistics.update(stats)
        self.send_statistics_update()

    def send_statistics_update(self):
        try:
            message = Message(TK_KDS_UPDATE_STATISTICS, DataType.json, json.dumps(self.statistics), 5000000)
            self.message_bus.send_message("NKDSCTRL", message)
        except:
            pass

    class PublishWaiter(object):
        def __init__(self, production_manager, order, wait_time):
            self.production_manager = production_manager
            self.order = order
            self.wait_time = wait_time
            self.condition = Condition()
            self.active = True

        def wait_and_publish(self):
            t = Thread(target=self._wait_and_publish, name="PublishWaiter")
            t.daemon = True
            t.start()

        def deactivate(self):
            self.active = False
            with self.condition:
                self.condition.notify_all()

        def _wait_and_publish(self):
            with self.condition:
                self.condition.wait(self.wait_time)

            if self.active:
                self.production_manager.publish_order(self.order)

    class PurgeWaiter(object):
        def __init__(self, production_manager, logger):
            self.production_manager = production_manager
            self.logger = logger
            self.wait_time = production_manager.purge_interval
            self.orders_life_time = production_manager.orders_life_time
            self.production_repository = production_manager.production_repository
            self.orders = production_manager.orders
            self.condition = Condition()
            self.active = True

        def deactivate(self):
            self.active = False
            with self.condition:
                self.condition.notify_all()

        def purge_orders_and_wait(self):
            t = Thread(target=self._purge_orders_and_wait, name="PurgeWaiter")
            t.daemon = True
            t.start()

        def _purge_orders_and_wait(self):
            while self.active:
                try:
                    self.logger.debug("Starting thread!")
                    with self.condition:
                        sleep_time = self.wait_time * 60
                        self.logger.debug("Sleeping for {} seconds".format(sleep_time))
                        self.condition.wait(sleep_time)
                        
                    self.purge_orders()
                except (BaseException, Exception) as _:
                    self.logger.exception("Error purging old orders")
                
        def purge_orders(self, all_orders=False):
            self.logger.info("Starting purge process...")
            
            if not all_orders:
                limit_date = datetime.now() - timedelta(minutes=self.orders_life_time)
                orders_to_purge = self.production_repository.get_orders_to_purge(limit_date)
            else:
                all_orders = self.production_repository.get_all_orders()
                orders_to_purge = [x.order_id for x in all_orders]
                
            self.logger.info("Found {} orders to purge".format(len(orders_to_purge)))
            
            if len(orders_to_purge) != 0:
                self.production_manager.handle_command(PurgeOrdersCommand(orders_to_purge))
