import salecomp.repository
from mwhelper import BaseRepository
from salecomp.model import ProductPart, DefaultOption
from typing import Dict, List


class ProductRepository(salecomp.repository.ProductRepository, BaseRepository):
    def __init__(self, mb_context):
        super(ProductRepository, self).__init__(mb_context)
        self.menus = self.load_menus()  # type: Dict[int, int]
        self.options = self.load_options()  # type: Dict[int, Dict[int, int]]
        self.parts = self.load_parts()  # type: Dict[int, List[ProductPart]]
        self.default_options = self.load_default_options()  # type: Dict[int, List[DefaultOption]]

    def is_menu_valid(self, menu_id):
        return menu_id in self.menus

    def is_option(self, part_code):
        return part_code in self.options

    def is_valid_solution(self, option_part_code, part_code):
        if option_part_code not in self.options:
            return False
        if part_code not in self.options[option_part_code]:
            return False

        return True

    def get_max_quantity(self, part_code, son_part_code):
        return self.parts[part_code][son_part_code].max_quantity

    def get_parts(self, part_code):
        return list(self.parts[part_code].itervalues())

    def get_default_options(self, part_code):
        if part_code not in self.default_options:
            return None
        return self.default_options[part_code]

    def load_menus(self):
        return self.get_product_dict_by_product_type(3)

    def load_options(self):
        def inner_func(conn):
            options = {}
            cursor = conn.select(self.get_options_query)
            for row in cursor:
                option_part_code = int(row.get_entry(0))
                solution_part_code = int(row.get_entry(1))
                if option_part_code not in options:
                    options[option_part_code] = {}

                options[option_part_code][solution_part_code] = solution_part_code
            return options

        return self.execute_with_connection(inner_func)

    def load_parts(self):
        def inner_func(conn):
            parts = {}
            cursor = conn.select(self.get_parts_query)
            for row in cursor:
                part = ProductPart(product_code=int(row.get_entry(0)),
                                   part_code=int(row.get_entry(1)),
                                   min_quantity=int(row.get_entry(2)),
                                   max_quantity=int(row.get_entry(3)),
                                   default_quantity=int(row.get_entry(4)))

                if part.product_code not in parts:
                    parts[part.product_code] = {}

                parts[part.product_code][part.part_code] = part

            return parts

        return self.execute_with_connection(inner_func)

    def get_product_dict_by_product_type(self, product_type):
        def inner_func(conn):
            products = {}
            cursor = conn.select(self.get_menus_query.format(product_type))
            for row in cursor:
                products[int(row.get_entry(0))] = int(row.get_entry(0))
            return products

        return self.execute_with_connection(inner_func)

    def load_default_options(self):
        solution_option = {}
        for option_part_code in self.options.iterkeys():
            for solution_part_code in self.options[option_part_code].iterkeys():
                solution_option[solution_part_code] = option_part_code
        def inner_func(conn):
            default_options = {}
            cursor = conn.select(self.get_default_options_from_custom_params_query)
            for row in cursor:
                combo_part_code = int(row.get_entry(0))
                default_solutions = []
                for solution in row.get_entry(1).split('|'):
                    default_solutions.append(int(solution))

                created_default_options = {}  # type: Dict[int, DefaultOption]
                if combo_part_code in self.parts:
                    for part in list(self.parts[combo_part_code].itervalues()):
                        if part.part_code in self.options:
                            for solution in default_solutions:
                                if solution in self.options[part.part_code]:
                                    if part.part_code in created_default_options:
                                        created_default_options[part.part_code].part_codes.append(solution)
                                    else:
                                        created_default_options[part.part_code] = \
                                            DefaultOption(part.part_code, [solution])

                if len(created_default_options) > 0:
                    default_options[combo_part_code] = list(created_default_options.itervalues())
            return default_options

        return self.execute_with_connection(inner_func)

    get_menus_query = \
"""select p.ProductCode 
from Product p
inner join ProductKernelParams pkp
on p.ProductCode = pkp.ProductCode
where pkp.ProductType = 3"""

    get_options_query = \
"""SELECT p.ProductCode, pc.ProductCode
from Product p
inner join ProductKernelParams pkp
on p.ProductCode = pkp.ProductCode
inner join ProductClassification pc
on p.ProductCode = pc.ClassCode
where pkp.ProductType = 1"""

    get_parts_query = \
"""
select ProductCode, PartCode, MinQty, MaxQty, DefaultQty
from ProductPart
"""

    get_default_options_from_custom_params_query = \
"""select ProductCode, CustomParamValue
from ProductCustomParams
where CustomParamId = 'defaultoption'
"""