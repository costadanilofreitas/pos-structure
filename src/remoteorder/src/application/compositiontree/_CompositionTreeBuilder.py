# -*- coding: utf-8 -*-

from application.compositiontree import CompositionTree, CompositionType, ProductNode, ProductPart, ProductRepository
from application.customexception import CompositionTreeError, CompositionTreeException
from typing import List


class CompositionTreeBuilder(object):
    def __init__(self, product_repository):
        # type: (ProductRepository) -> None

        self.product_repository = product_repository
        self.all_combos = self.product_repository.get_all_combos()
        self.all_products = self.product_repository.get_all_products()
        self.all_options = self.product_repository.get_all_options()

        self.all_combo_products = self.product_repository.get_all_combo_products()
        self.all_combo_options = self.product_repository.get_all_combo_options()
        self.all_combo_combos = self.product_repository.get_all_combo_combos()
        self.all_product_ingredients = self.product_repository.get_all_product_ingredients()
        self.all_option_products = self.product_repository.get_all_option_products()
        self.all_default_products = self.product_repository.get_default_products()

    def get_composition_tree(self, part_code, product_part=None, parent_composition=None, unavailable_list=[]):
        # type: (unicode, ProductPart, CompositionTree, List[unicode]) -> CompositionTree
        composition_tree = CompositionTree()
        composition_tree.parent = parent_composition
        composition_tree.product = ProductNode(
            part_code=part_code,
            type=None,
            default_qty=product_part.default_qty if product_part else None,
            min_qty=product_part.min_qty if product_part else None,
            max_qty=product_part.max_qty if product_part else None,
            current_qty=None,
            price=None)

        composition_tree.sons = []
        composition_tree.product.enabled = str(part_code) not in unavailable_list

        if parent_composition and composition_tree.product.default_qty is None:
            if parent_composition.parent:
                key = (parent_composition.parent.product.part_code, parent_composition.product.part_code)
                if key in self.all_default_products:
                    if part_code in self.all_default_products[key]:
                        composition_tree.product.default_qty = 1
                    else:
                        composition_tree.product.default_qty = 0
            else:
                composition_tree.product.default_qty = 0

        parent_is_option = parent_composition and parent_composition.product.type == CompositionType.OPTION
        parent_is_product = parent_composition and parent_composition.product.type == CompositionType.PRODUCT
        is_mandatory_product = (composition_tree.product.default_qty or 0) > 0 or (composition_tree.product.min_qty or 0) > 0
        disabled_product = composition_tree.product.enabled is not True

        if part_code in self.all_combos:
            composition_tree.product.type = CompositionType.COMBO

            if part_code in self.all_combo_products:
                combo_products = self.all_combo_products[part_code]
                for combo_product in combo_products:
                    son_composition = self.get_composition_tree(combo_product.part_code, combo_product, composition_tree, unavailable_list)
                    composition_tree.sons.append(son_composition)

                    # handle disabled
                    if son_composition.product.enabled is False:
                        composition_tree.product.enabled = False

            if part_code in self.all_combo_options:
                combo_options = self.all_combo_options[part_code]
                for combo_option in combo_options:
                    son_composition = self.get_composition_tree(combo_option.part_code, combo_option, composition_tree, unavailable_list)
                    composition_tree.sons.append(son_composition)

                    # handle disabled
                    is_mandatory_option = (son_composition.product.default_qty or 0) > 0 or (son_composition.product.min_qty or 0) > 0
                    if is_mandatory_option and son_composition.product.enabled is False:
                        composition_tree.product.enabled = False

            if part_code in self.all_combo_combos:
                combo_combos = self.all_combo_combos[part_code]
                for combo_combo in combo_combos:
                    son_composition = self.get_composition_tree(combo_combo.part_code, combo_combo, composition_tree, unavailable_list)
                    composition_tree.sons.append(son_composition)

                    # handle disabled
                    if son_composition.product.enabled is False:
                        composition_tree.product.enabled = False

        elif part_code in self.all_products:
            composition_tree.product.type = CompositionType.PRODUCT

            if part_code in self.all_product_ingredients:
                product_ingredients = self.all_product_ingredients[part_code]
                for product_ingredient in product_ingredients:
                    son_composition = self.get_composition_tree(product_ingredient.part_code, product_ingredient, composition_tree, unavailable_list)
                    composition_tree.sons.append(son_composition)

                    # handle disabled
                    is_mandatory_ingredient = (son_composition.product.default_qty or 0) > 0 or (son_composition.product.min_qty or 0) > 0
                    if is_mandatory_ingredient and son_composition.product.enabled is False:
                        composition_tree.product.enabled = False

            # handle disabled
            if disabled_product and parent_composition:
                if parent_is_product and is_mandatory_product:
                    parent_composition.product.enabled = False

                elif parent_is_option and parent_composition.parent:
                    grandfather_is_product = parent_composition.parent.product.type == CompositionType.PRODUCT

                    if is_mandatory_product and grandfather_is_product:
                        parent_composition.parent.product.enabled = False

        elif part_code in self.all_options:
            composition_tree.product.type = CompositionType.OPTION

            if part_code in self.all_option_products:
                option_products = self.all_option_products[part_code]
                for option_product in option_products:
                    son_composition = self.get_composition_tree(option_product.part_code, option_product, composition_tree, unavailable_list)
                    son_composition.product.max_qty = composition_tree.product.max_qty
                    composition_tree.sons.append(son_composition)

                # handle disabled
                all_sons_disabled = all([not x.product.enabled for x in composition_tree.sons])
                sum_of_sons_max_qty = sum([x.product.max_qty or 0 for x in composition_tree.sons if x.product.enabled])
                min_qty = (composition_tree.product.min_qty or 0) or (composition_tree.product.default_qty or 0)

                if all_sons_disabled:
                    composition_tree.product.enabled = False

                elif min_qty > sum_of_sons_max_qty:
                    composition_tree.product.enabled = False
                    if parent_composition:
                        composition_tree.parent.product.enabled = False

        else:
            message = "$PART_CODE_NOT_A_PRODUCT|{}".format(part_code)
            raise CompositionTreeException(CompositionTreeError.InvalidPartCode, message)

        return composition_tree
