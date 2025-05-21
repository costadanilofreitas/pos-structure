# -*- coding: utf-8 -*-

from application.compositiontree import CompositionTree, ProductNode, CompositionType, ProductRepository
from application.customexception import InvalidSonException, OrderValidationException, OrderValidationError, \
    ProductUnavailableException, InvalidQuantityException
from application.model import OrderItem
from typing import Union, Tuple, Optional


class CompositionTreeValidator(object):
    def __init__(self, product_repository):
        # type: (ProductRepository) -> None

        self.all_products_name = product_repository.get_product_name_dictionary()

    @staticmethod
    def create_product(parent, item, quantity, price, default_qty=True):
        created_son = CompositionTree()
        created_son.parent = parent
        created_son.sons = []
        created_son.product = ProductNode(
            part_code=item.product.part_code,
            type=item.product.type,
            default_qty=item.product.default_qty if default_qty else None,
            min_qty=item.product.min_qty,
            max_qty=item.product.max_qty,
            current_qty=quantity,
            price=price)
        return created_son

    def validate_order_composition(self, composition_tree, order_item):
        # type: (CompositionTree, OrderItem) -> CompositionTree
        if order_item.part_code != composition_tree.product.part_code:
            message = "Received a composition tree with a different root partCode"
            raise OrderValidationException(OrderValidationError.InternalError, message)

        new_composition_tree = self.create_product(None, composition_tree, order_item.quantity, order_item.price, False)
        new_composition_tree.product.comment = order_item.comment

        if order_item.parts is not None and len(order_item.parts) != 0:
            if composition_tree.sons is None or len(composition_tree.sons) == 0:
                message = "$PART_CODE_NOT_A_VALID_SON|{}|{}".format(order_item.parts[0].part_code, order_item.part_code)
                raise InvalidSonException(OrderValidationError.InvalidPartForParentPartCode, message)

            for part in order_item.parts:
                self._process_part(part, composition_tree, new_composition_tree)

        self._check_min_quantity(new_composition_tree, composition_tree)

        return new_composition_tree

    def _process_part(self, part, composition_tree, new_composition_tree):
        price = part.price or None
        new_composition_son, composition_tree_branch = self._find_son(part.part_code, part.quantity, composition_tree, new_composition_tree, price)

        if new_composition_son is not None and len(filter(lambda son: son.product.part_code == new_composition_son.product.part_code, new_composition_tree.sons)) == 0:
            # Só adicionamos caso não tenha sido previamente adicionado por outro produto
            new_composition_tree.sons.append(new_composition_son)

        if part.parts is not None and len(part.parts) > 0:
            positioned_new_composition_son, positioned_composition_tree = self._position_trees(new_composition_son, composition_tree_branch, part.part_code)

            for subpart in part.parts:
                self._process_part(subpart, positioned_composition_tree, positioned_new_composition_son)

    def _find_son(self, part_code, quantity, composition_tree, new_composition_tree, price):
        # type: (unicode, int, CompositionTree, CompositionTree, float) -> Union[Tuple[CompositionTree, CompositionTree], Tuple[None, None]]
        if composition_tree.sons is None or len(composition_tree.sons) == 0:
            message = "$PART_CODE_NOT_A_VALID_SON|{}|{}".format(part_code, composition_tree.product.part_code)
            raise InvalidSonException(OrderValidationError.InvalidPartForParentPartCode, message)

        # Vamos procurar se o part_code já foi adicionado na nova árvore
        new_composition_son_list = filter(lambda sonx: sonx.product.part_code == part_code, new_composition_tree.sons)
        if len(new_composition_son_list) > 1:
            message = "Two root nodes with the same partCode already in the tree"
            raise OrderValidationException(OrderValidationError.InternalError, message)

        if len(new_composition_son_list) == 1:
            # O part_code já foi adicionado na árvore
            new_composition_son = new_composition_son_list[0]

            if new_composition_son.product.current_qty + quantity > new_composition_son.product.max_qty:
                message = "The max quantity of item {} was exceeded".format(new_composition_son.product.part_code)
                raise InvalidQuantityException(OrderValidationError.MaxQuantityExceeded, message)

            self._check_option_quantity(new_composition_son, new_composition_son.parent, quantity)

            new_composition_son.product.current_qty += quantity
            if new_composition_son.product.current_qty < 0:
                new_composition_son.product.current_qty = 0

            return None, None
        else:
            # O part_code ainda não foi adicionado na árvore
            son = next((son for son in composition_tree.sons if son.product.part_code == part_code), None)
            if son is not None:
                # O part_code é um dos nossos filhos diretos
                if son.product.enabled is not True:
                    message = "The part code {} is not enabled".format(son.product.part_code)
                    raise ProductUnavailableException(OrderValidationError.InternalError, message)

                create_quantity = quantity if son.product.type != CompositionType.OPTION else 0
                new_composition_son = self.create_product(new_composition_tree, son, create_quantity, price, True)

                product = new_composition_son.product
                new_composition_son.product.enabled = son.product.enabled
                if quantity < 0 and son.product.default_qty == 0:
                    message = "The partCode {} cannot be removed because the default quantity is 0"
                    message = message.format(product.part_code)
                    raise InvalidQuantityException(OrderValidationError.CannotRemoveItemNotInDefault, message)

                added_quantity = 0
                if son.product.type != CompositionType.OPTION:
                    default_quantity = product.default_qty if product.default_qty is not None else 0
                    added_quantity = product.current_qty + default_quantity
                    added_quantity = son.product.max_qty if added_quantity > son.product.max_qty else added_quantity
                    added_quantity = 0 if added_quantity < 0 else added_quantity
                    product.current_qty = added_quantity

                self._check_option_quantity(new_composition_son, new_composition_son.parent, added_quantity)

                # Acabamos de criar um nó, então retornamos para que ele seja adicionado ao pai
                return new_composition_son, son

        # Só chegamos aqui se o part_code não é um filho direto do nó que estamos. Vamos procurá-lo em todos os fihos
        invalid_quantity_exception = None
        for son in composition_tree.sons:
            try:
                intermediate_son_list = filter(lambda new_son: new_son.product.part_code == son.product.part_code, new_composition_tree.sons)
                if len(intermediate_son_list) > 1:
                    message = "Two intermediate nodes with the same partCode already in the tree"
                    raise OrderValidationException(OrderValidationError.InternalError, message)

                if len(intermediate_son_list) == 1:
                    # Encontramos o nó que tem o part_code como filho, vamos retorná-lo
                    intermediate_son = intermediate_son_list[0]
                    if intermediate_son.product.enabled is False:
                        raise ProductUnavailableException(OrderValidationError.InternalError, "The part code {} is not enabled".format(intermediate_son.product.part_code))
                else:
                    # Não encontramos nenhum nó que tenha o part_code como filho, vamos criar um nó intermediário e procurar nos netos
                    create_quantity = 1 if son.product.type != CompositionType.OPTION else 0
                    intermediate_son = self.create_product(new_composition_tree, son, create_quantity, price, True)

                new_composition_son, _ = self._find_son(part_code, quantity, son, intermediate_son, price)
                if new_composition_son is not None:
                    # Apenas adicionamos filhos criados. Se nosso filho foi atualizado não precisamos adicionar
                    intermediate_son.sons.append(new_composition_son)

                # TODO: Criar teste para este caso
                # Apenas retornamos o nó intermeriário se ele foi criado
                if len(intermediate_son_list) != 1:
                    return intermediate_son, son
                else:
                    return None, None
            except InvalidQuantityException as ex:
                invalid_quantity_exception = ex
            except InvalidSonException as _:
                pass

        if invalid_quantity_exception:
            raise invalid_quantity_exception

        message = "$PART_CODE_NOT_A_VALID_SON|{}|{}".format(part_code, composition_tree.product.part_code)
        raise InvalidSonException(OrderValidationError.InvalidPartForParentPartCode, message)

    @staticmethod
    def _check_option_quantity(current_item, parent_item, quantity):
        if parent_item is not None and parent_item.product.type == CompositionType.OPTION:
            if parent_item.product.current_qty + quantity > parent_item.product.max_qty:
                message = "The max quantity of option {} was exceeded by the item {}"
                message = message.format(parent_item.product.part_code, current_item.product.part_code)
                raise InvalidQuantityException(OrderValidationError.MaxQuantityExceeded, message)
            parent_item.product.current_qty += quantity

    def _check_min_quantity(self, json_order_tree, composition_tree):
        # type: (CompositionTree, CompositionTree) -> None

        tree_product = composition_tree.product
        json_product = json_order_tree.product
        if tree_product.min_qty is not None and ((json_product.current_qty or 0) < tree_product.min_qty):
            json_product.current_qty = tree_product.min_qty

        if composition_tree.sons is not None:
            for tree_son in composition_tree.sons:
                json_item_son = self._get_item_son(json_order_tree, tree_son)
                if json_item_son is None:
                    if self._non_mandatory_product(tree_son.product):
                        continue

                    self._validate_if_option_has_no_mandatory_son(composition_tree, tree_son)
                    self._create_product(json_order_tree, tree_son)

                elif (json_item_son.product.current_qty or 0) > 0:
                    self._check_min_quantity(json_item_son, tree_son)

            self._validate_option_min_qty(json_order_tree, tree_product)

    @staticmethod
    def _get_item_son(json_order_tree, tree_son):
        # type: (CompositionTree, CompositionTree) -> Optional[CompositionTree]

        json_sons = json_order_tree.sons
        tree_son_part_code = tree_son.product.part_code
        return next((son for son in json_sons if son.product.part_code == tree_son_part_code), None)

    def _validate_option_min_qty(self, json_order_tree, tree_product):
        # type: (CompositionTree, ProductNode) -> None

        min_qty = tree_product.min_qty
        if tree_product.type == CompositionType.OPTION and min_qty > 0:
            product_sons_quantity = sum(son.product.current_qty or 0 for son in json_order_tree.sons)
            if min_qty > product_sons_quantity:
                part_code = tree_product.part_code
                product_name = part_code
                if part_code in self.all_products_name:
                    product_name += " (" + self.all_products_name[part_code] + ")"

                message = "$MIN_QTY_NOT_REACHED|{}|{}|{}".format(product_name, min_qty, product_sons_quantity)
                raise InvalidQuantityException(OrderValidationError.MinQuantityNotReached, message)

    def _create_product(self, json_order_tree, tree_son):
        # type: (CompositionTree, CompositionTree) -> None

        min_qty = tree_son.product.min_qty
        price = tree_son.product.price
        create_with_default_quantity = tree_son.product.type == CompositionType.OPTION
        created_son = self.create_product(json_order_tree, tree_son, min_qty, price, create_with_default_quantity)
        json_order_tree.sons.append(created_son)

        self._create_option_sons_with_default_qty(created_son, tree_son)
        self._check_min_quantity(created_son, tree_son)

    def _create_option_sons_with_default_qty(self, created_son, tree_son):
        # type: (CompositionTree, CompositionTree) -> None

        if tree_son.product.type == CompositionType.OPTION:
            for grand_son in tree_son.sons:
                if grand_son.product.default_qty > 0:
                    create_quantity = grand_son.product.default_qty
                    created_grand_son = self.create_product(created_son, grand_son, create_quantity,
                                                            grand_son.product.price, False)
                    created_son.sons.append(created_grand_son)
                    self._check_min_quantity(created_grand_son, grand_son)

    @staticmethod
    def _validate_if_option_has_no_mandatory_son(composition_tree, tree_son):
        # type: (CompositionTree, CompositionTree) -> None

        if composition_tree.product.type == CompositionType.OPTION:
            message = "The min quantity of the item {0}->{1} was not reached"
            message = message.format(composition_tree.product.part_code, tree_son.product.part_code)
            raise InvalidQuantityException(OrderValidationError.MinQuantityNotReached, message)

    def _position_trees(self, new_composition_tree, composition_tree, part_code):
        # type: (CompositionTree, CompositionTree, str) -> Union[Tuple[CompositionTree, CompositionTree], Tuple[None, None]] # noqa

        if part_code == new_composition_tree.product.part_code:
            return new_composition_tree, composition_tree

        # Procuramos os filhos diretos
        for new_son in new_composition_tree.sons:
            if new_son.product.part_code == part_code:
                for son in composition_tree.sons:
                    if son.product.part_code == new_son.product.part_code:
                        return new_son, son

        # O part_code não é um filho direto, vamos procurar nas subarvores
        for new_son in new_composition_tree.sons:
            for son in composition_tree.sons:
                if new_son.product.part_code == son.product.part_code:
                    positioned_new_son, positioned_son = self._position_trees(new_son, son, part_code)
                    if positioned_new_son is not None:
                        return positioned_new_son, positioned_son

        return None, None

    @staticmethod
    def _non_mandatory_product(product):
        # type: (Optional[ProductNode]) -> bool

        return product.min_qty <= 0
