# -*- coding: utf-8 -*-

import base64
import json
import logging
import zlib

from application.compositiontree import CompositionTreeBuilder, CompositionTree, CompositionTreeJsonEncoder, \
    ProductRepository
from application.services import PriceService
from typing import Union, Dict

logger = logging.getLogger("RemoteOrder")


class MenuBuilder(object):
    def __init__(self, composition_tree_builder, price_service, product_repository):
        # type: (CompositionTreeBuilder, PriceService, ProductRepository) -> None
        self.composition_tree_builder = composition_tree_builder
        self.price_service = price_service
        self.product_repository = product_repository
        self.cached_menu = None  # type: Union[unicode, None]
        self.unavailable_items = []

    def get_menu(self, new_unavailable_items=None, without_combos=False):
        all_part_codes = []
        all_part_codes.extend(self.product_repository.get_all_products())
        if not without_combos:
            all_part_codes.extend(self.product_repository.get_all_combos())

        name_dictionary = self.product_repository.get_product_name_dictionary()
        menu = []
        for part_code in all_part_codes:
            try:
                unavailable_list = new_unavailable_items if new_unavailable_items else self.unavailable_items
                tree = self.composition_tree_builder.get_composition_tree(part_code,
                                                                          unavailable_list=unavailable_list)

                self._price_tree(tree)
                self._price_combo(tree)
                self._price_father_combo(tree)

                self._add_product_names_to_tree(tree, name_dictionary)
                menu.append(tree)
            except Exception as _:
                logger.exception("Error building composition tree for PartCode: {}".format(part_code))
        return menu

    def get_menu_as_json(self, new_unavailable_items=None, cached=True, without_combos=False):
        if self.cached_menu is None or cached is False:
            menu_tree = self.get_menu(new_unavailable_items=new_unavailable_items, without_combos=without_combos)

            # Making partial DUMPS to be Memory Efficient (Memory Error Exception)
            menu = [json.dumps(menu_item, encoding="utf-8", cls=CompositionTreeJsonEncoder) for menu_item in menu_tree]
            menu_json = "[" + ",".join(menu) + "]"

            with open("menu.json", "w") as f:
                f.write(menu_json)

            if cached:
                compress_obj = zlib.compressobj(zlib.Z_BEST_COMPRESSION, zlib.DEFLATED, 31)
                zipped_menu = compress_obj.compress(menu_json)
                zipped_menu += compress_obj.flush()
                base64_zipped_menu = base64.b64encode(zipped_menu)

                self.cached_menu = base64_zipped_menu
            else:
                return menu_json

        return self.cached_menu

    def get_rupture_menu(self, unavailable_list, without_combos):
        menu_tree = self.get_menu(unavailable_list, without_combos)
        menu = {item.product.part_code: (item.product.name, item.product.enabled) for item in menu_tree}

        return menu

    def _price_tree(self, tree, parent_context=""):
        # type: (CompositionTree, unicode) -> None
        prices = self.price_service.get_best_price(parent_context, tree.product.part_code, [u"EI", u"DL"])
        if prices is not None:
            tree.product.unit_price = prices[0]
            tree.product.added_unit_price = prices[1]

        if parent_context == "":
            new_context = tree.product.part_code
        else:
            new_context = parent_context + "." + tree.product.part_code
        for son in tree.sons:
            self._price_tree(son, new_context)

    def _price_combo(self, tree, parent=None, grand_parent=None):
        # type: (CompositionTree, CompositionTree, CompositionTree) -> None
        if parent is not None and parent.product.type == "Combo" and tree.product.type == "Product" \
                and tree.product.min_qty is not None \
                and tree.product.unit_price is not None:
            if parent.product.unit_price is None:
                parent.product.unit_price = tree.product.min_qty * tree.product.unit_price
            else:
                parent.product.unit_price += tree.product.min_qty * tree.product.unit_price

        if grand_parent is not None and \
                        grand_parent.product.type == "Combo" and \
                        parent.product.type == "Option" and \
                        tree.product.type == "Product" and \
                        tree.product.default_qty is not None and \
                        tree.product.unit_price is not None:
            if grand_parent.product.unit_price is None:
                grand_parent.product.unit_price = tree.product.default_qty * tree.product.unit_price
            else:
                grand_parent.product.unit_price += tree.product.default_qty * tree.product.unit_price

        for son in tree.sons:
            self._price_combo(son, tree, parent)

    def _price_father_combo(self, tree, parent=None):
        # type: (CompositionTree, CompositionTree) -> None
        for son in tree.sons:
            self._price_father_combo(son, tree)

        if parent is not None and parent.product.type == "Combo" and tree.product.type == "Combo":
            if parent.product.unit_price is None:
                parent.product.unit_price = tree.product.unit_price
            else:
                parent.product.unit_price += tree.product.unit_price or 0

    def _add_product_names_to_tree(self, tree, name_dictionary):
        # type: (CompositionTree, Dict[unicode, unicode]) -> None
        tree.product.name = name_dictionary[tree.product.part_code]

        for son in tree.sons:
            self._add_product_names_to_tree(son, name_dictionary)
