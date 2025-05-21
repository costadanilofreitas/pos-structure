from enum import Enum
from salecomp.model import Line
from salecomp.repository import OrderRepository, ProductRepository
from typing import List, Optional, Tuple, Dict
from salecomp.model.exception import *


class DoOptionInteractor(object):
    def __init__(self, order_repository, product_repository):
        # type: (OrderRepository, ProductRepository) -> None
        self.order_repository = order_repository
        self.product_repository = product_repository

        self.line = None
        self.option_line = None
        self.option_part_code = None
        self.solution_part_code = None
        self.solution_quantity_on_option = 0

        self.change_tracker = ChangeTracker()

    def execute(self, pos_id, order_id, line_number, item_id, quantity):
        # type: (int, int, int, str, int) -> None
        self.validate_input(pos_id, order_id, line_number, item_id, quantity)

        self.sell_option(line_number, self.option_line, self.option_part_code, self.solution_part_code, item_id, quantity)

        for change in self.change_tracker.get_changes():
            if change.type == ChangeType.add:
                self.order_repository.add_line(change.line)
            elif change.type == ChangeType.update:
                self.order_repository.update_line(change.line)
            else:
                self.order_repository.delete_sons(change.line)

    def sell_option(self, line_number, option_line, option_part_code, solution_part_code, item_id, quantity):
        self.insert_option(item_id, line_number, option_line, option_part_code, quantity)

        solution_line = self.get_node_by_item_id(self.line, self.remove_menu(item_id))
        if solution_line is None:
            self.insert_new_solution(item_id, line_number, option_line, quantity, solution_part_code)
        else:
            self.change_solution_quantity(solution_line, option_line, quantity)

    def insert_option(self, item_id, line_number, option_line, option_part_code, quantity):
        if option_line is None:
            option_item_id = self.separate_last_part_code(self.separate_last_part_code(item_id)[1])[1]
            self.create_option(line_number, option_item_id, option_part_code, quantity)

    def change_solution_quantity(self, leaf_product, option_line, quantity):
        leaf_product.quantity = quantity
        self.order_repository.update_line(leaf_product)

        if option_line is not None:
            option_line.quantity += (quantity - self.solution_quantity_on_option)
            self.change_tracker.add_change(Change(ChangeType.update, option_line))

        if leaf_product.quantity == 0:
            self.change_tracker.add_change(Change(ChangeType.delete_sons, leaf_product))

    def insert_new_solution(self, item_id, line_number, option_line, quantity, solution_part_code):
        new_line = Line(line_number, self.separate_last_part_code(item_id)[1], solution_part_code, quantity)
        self.change_tracker.add_change(Change(ChangeType.add, new_line))

        if option_line is not None:
            option_line.quantity += (quantity - self.solution_quantity_on_option)
            self.change_tracker.add_change(Change(ChangeType.update, option_line))

        self.insert_parts(line_number, new_line, solution_part_code)
        self.insert_default_options(item_id, line_number, new_line)

    def insert_default_options(self, item_id, line_number, new_line):
        default_options = self.product_repository.get_default_options(new_line.part_code)
        if default_options is not None:
            for default_option in default_options:
                for part in default_option.part_codes:
                    part_item_id = item_id + "." + str(default_option.option_code) + "." + str(part)
                    self.sell_option(line_number, None, default_option.option_code, part, part_item_id, 1)

    def insert_parts(self, line_number, new_line, solution_part_code):
        parts = self.product_repository.get_parts(solution_part_code)
        if parts is not None:
            for part in parts:
                part_item_id = new_line.item_id + "." + str(new_line.part_code)
                self.create_option(line_number, part_item_id, part.part_code, part.default_quantity)

    def create_option(self, line_number, item_id, option_part_code, quantity):
        new_option_line = Line(line_number, item_id, option_part_code, quantity)
        self.change_tracker.add_change(Change(ChangeType.add, new_option_line))

    def validate_input(self, pos_id, order_id, line_number, item_id, quantity):
        item_path = self.validate_item_id(item_id)
        self.validate_menu(item_path)
        self.validate_option_part_code(item_path)
        self.validate_solution_part_code(item_path)

        order = self.validate_order(order_id, pos_id)
        self.validate_line_number(line_number, order)
        self.line = order.lines[line_number - 1]

        node_item_id = self.get_product_code(item_id)
        leaf = self.get_node_by_item_id(self.line, node_item_id)
        if leaf is None:
            raise ParentNotFoundException()

        option_parent_part_code = int(item_path[-3])
        max_quantity = self.product_repository.get_max_quantity(option_parent_part_code, self.option_part_code)
        used_option_quantity = 0
        self.option_line = self.get_correct_son(leaf, self.option_part_code)
        if self.option_line is not None:
            used_option_quantity = 0
            for son in self.option_line.lines:
                if son.part_code != self.solution_part_code:
                    used_option_quantity += son.quantity
                else:
                    self.solution_quantity_on_option = son.quantity

        new_quantity = used_option_quantity + quantity
        if new_quantity > max_quantity:
            raise OptionMaxQuantityExceeded(option_parent_part_code, self.option_part_code, max_quantity, new_quantity)

    def get_product_code(self, item_id):
        return self.remove_menu(item_id).replace(".{}.{}".format(self.option_part_code, self.solution_part_code), "")

    def validate_order(self, order_id, pos_id):
        order = self.order_repository.get_order(pos_id, order_id)
        if order is None:
            raise OrderNotFound()
        return order

    def validate_solution_part_code(self, item_path):
        self.solution_part_code = int(item_path[-1])
        if not self.product_repository.is_valid_solution(self.option_part_code, self.solution_part_code):
            raise NotValidSolution(self.option_part_code, self.solution_part_code)

    def validate_option_part_code(self, item_path):
        self.option_part_code = int(item_path[-2])
        if not self.product_repository.is_option(self.option_part_code):
            raise ParentIsNotAnOption(self.option_part_code)

    def validate_menu(self, item_path):
        menu_id = item_path[0]
        if not self.product_repository.is_menu_valid(menu_id):
            raise InvalidMenu()

    def get_node_by_item_id(self, line, item_id):
        # type: (Line, List[int]) -> Optional[Line]
        part_code, remaining_item_id = self.separate_first_part_code(item_id)
        if line.part_code != part_code:
            return None

        if remaining_item_id is None:
            return line

        son_part_code, son_remaining_item_id = self.separate_first_part_code(remaining_item_id)
        son = self.get_correct_son(line, son_part_code)
        if son is None:
            return None

        return self.get_node_by_item_id(son, remaining_item_id)

    @staticmethod
    def validate_line_number(line_number, order):
        if line_number > len(order.lines):
            raise LineNotFound()

    @staticmethod
    def validate_item_id(item_id):
        item_path = item_id.split(".")
        if len(item_path) <= 3:
            raise InvalidItemId()
        return item_path

    @staticmethod
    def get_correct_son(line, part_code):
        # type: (Line, int) -> Optional[Line]
        for son in line.lines:
            if son.part_code == part_code:
                return son
        return None

    @staticmethod
    def separate_first_part_code(item_id):
        # type: (str) -> Tuple[int, Optional[str]]
        index = item_id.find(".")
        if index < 0:
            return int(item_id), None
        else:
            return int(item_id[:index]), item_id[index + 1:]

    @staticmethod
    def separate_last_part_code(item_id):
        # type: (str) -> Tuple[int, Optional[str]]
        index = item_id.rfind(".")
        return int(item_id[index + 1:]), item_id[:index]

    @staticmethod
    def remove_menu(item_id):
        index = item_id.find(".")
        return item_id[index + 1:]


class ChangeType(Enum):
    add = 1,
    update = 2,
    delete_sons = 3


class Change(object):
    def __init__(self, type, line):
        self.type = type
        self.line = line

    def get_key(self):
        return self.line.item_id, self.line.part_code


class ChangeTracker(object):
    def __init__(self):
        self.changes = []
        self.changes_dict = {}  # type: Dict[Tuple[str, int], Change]

    def add_change(self, change):
        if change.get_key() in self.changes_dict:
            current_change = self.changes_dict[change.get_key()]

            if current_change.type == ChangeType.add and change.type == ChangeType.add:
                current_change.line.quantity += change.line.quantity
            else:
                current_change.line = change.line
        else:
            self.changes.append(change)
            self.changes_dict[change.get_key()] = change

    def get_changes(self):
        return self.changes
