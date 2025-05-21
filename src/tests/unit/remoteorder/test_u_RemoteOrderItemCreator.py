import unittest
import mock
from remoteorder.model import RemoteOrder, PickUpInfo, CurrentOrderItem
from remoteorder.repository import OrderRepository
from remoteorder.compositiontree import CompositionTree, ProductNode, CompositionType
from remoteorder import PriceService, RemoteOrderItemCreator


# TODO: testar mais de um item na order
class CreateCurrentOrderItemsTestCase(unittest.TestCase):
    def __init__(self, methodName):
        super(CreateCurrentOrderItemsTestCase, self).__init__(methodName)

        self.order_repository = mock.NonCallableMagicMock(spec=OrderRepository)
        self.price_service = mock.NonCallableMagicMock(spec=PriceService)
        self.price_service.get_best_price_key = self._fake_get_price_key

        self.remote_order_item_creator = RemoteOrderItemCreator(self.order_repository, self.price_service)

    def test_ComboWithProduct_OrderRepositoryCalledWithEachLine(self):
        remote_order = RemoteOrder()
        remote_order.pickup = PickUpInfo()
        remote_order.pickup.company = ""

        combo_whopper_tree = CompositionTree()
        combo_whopper_tree.product = ProductNode(part_code="1051", type=CompositionType.COMBO, default_qty=None, current_qty=1, min_qty=None, max_qty=None)
        combo_whopper_tree.sons = []

        whopper_tree = CompositionTree()
        whopper_tree.product = ProductNode(part_code="1050", type=CompositionType.PRODUCT, default_qty=1, current_qty=1, min_qty=1, max_qty=1)
        whopper_tree.sons = []
        combo_whopper_tree.sons.append(whopper_tree)

        self.remote_order_item_creator.create_current_order_items(1, 1, [combo_whopper_tree])
        call_args = self.order_repository.insert_current_order_item.call_args

        self.assertEqual(call_args[0][0], 1)

        combo = next((current_order_item for current_order_item in call_args[0][1] if current_order_item.part_code == "1051"), None)  # type: CurrentOrderItem
        self.assertIsNotNone(combo)
        self.assertEqual(combo.order_id, 1)
        self.assertEqual(combo.line_number, 1)
        self.assertEqual(combo.item_id, "1")
        self.assertEqual(combo.level, 0)
        self.assertEqual(combo.part_code, "1051")
        self.assertEqual(combo.ordered_quantity, 1)
        self.assertIsNone(combo.last_ordered_quantity)
        self.assertEqual(combo.included_quantity, 0)
        self.assertEqual(combo.decremented_quantity, 0)
        self.assertIsNone(combo.price_key)
        self.assertEqual(combo.discount_ammount, 0.0)
        self.assertEqual(combo.surcharge_ammount, 0.0)
        self.assertEqual(combo.only_flag, 0)
        self.assertIsNone(combo.overwrittern_unit_price)
        self.assertIsNone(combo.default_qty)

        whopper = next((current_order_item for current_order_item in call_args[0][1] if current_order_item.part_code == "1050"), None)  # type: CurrentOrderItem
        self.assertIsNotNone(whopper)
        self.assertEqual(whopper.order_id, 1)
        self.assertEqual(whopper.line_number, 1)
        self.assertEqual(whopper.item_id, "1.1051")
        self.assertEqual(whopper.level, 1)
        self.assertEqual(whopper.part_code, "1050")
        self.assertEqual(whopper.ordered_quantity, 1)
        self.assertIsNone(whopper.last_ordered_quantity)
        self.assertEqual(whopper.included_quantity, 1)
        self.assertEqual(whopper.decremented_quantity, 0)
        self.assertEqual(whopper.price_key, "1050_price_key")
        self.assertEqual(whopper.discount_ammount, 0.0)
        self.assertEqual(whopper.surcharge_ammount, 0.0)
        self.assertEqual(whopper.only_flag, 0)
        self.assertIsNone(whopper.overwrittern_unit_price)
        self.assertEqual(whopper.default_qty, 1)

    def test_ComboWithProductWithOptionWithIngredient_OrderRepositoryCalledWithEachLine(self):
        remote_order = RemoteOrder()
        remote_order.pickup = PickUpInfo()
        remote_order.pickup.company = ""

        combo_whopper_tree = CompositionTree()
        combo_whopper_tree.product = ProductNode(part_code="1051", type=CompositionType.COMBO, default_qty=None, current_qty=1, min_qty=None, max_qty=None)
        combo_whopper_tree.sons = []

        whopper_tree = CompositionTree()
        whopper_tree.product = ProductNode(part_code="1050", type=CompositionType.PRODUCT, default_qty=1, current_qty=1, min_qty=1, max_qty=1)
        whopper_tree.sons = []
        whopper_tree.parent = combo_whopper_tree
        combo_whopper_tree.sons.append(whopper_tree)

        ingredients_tree = CompositionTree()
        ingredients_tree.product = ProductNode(part_code="8200000", type=CompositionType.OPTION, default_qty=0, current_qty=1, min_qty=0, max_qty=99)
        ingredients_tree.sons = []
        ingredients_tree.parent = whopper_tree
        whopper_tree.sons.append(ingredients_tree)

        extra_maionese_tree = CompositionTree()
        extra_maionese_tree.product = ProductNode(part_code="27001", type=CompositionType.PRODUCT, default_qty=0, current_qty=1, min_qty=0, max_qty=9)
        extra_maionese_tree.sons = []
        extra_maionese_tree.parent = ingredients_tree
        ingredients_tree.sons.append(extra_maionese_tree)

        self.remote_order_item_creator.create_current_order_items(1, 1, [combo_whopper_tree])
        call_args = self.order_repository.insert_current_order_item.call_args

        self.assertEqual(call_args[0][0], 1)

        combo = next((current_order_item for current_order_item in call_args[0][1] if current_order_item.part_code == "1051"), None)  # type: CurrentOrderItem
        self.assertIsNotNone(combo)
        self.assertEqual(combo.order_id, 1)
        self.assertEqual(combo.line_number, 1)
        self.assertEqual(combo.item_id, "1")
        self.assertEqual(combo.level, 0)
        self.assertEqual(combo.part_code, "1051")
        self.assertEqual(combo.ordered_quantity, 1)
        self.assertIsNone(combo.last_ordered_quantity)
        self.assertEqual(combo.included_quantity, 0)
        self.assertEqual(combo.decremented_quantity, 0)
        self.assertIsNone(combo.price_key)
        self.assertEqual(combo.discount_ammount, 0.0)
        self.assertEqual(combo.surcharge_ammount, 0.0)
        self.assertEqual(combo.only_flag, 0)
        self.assertIsNone(combo.overwrittern_unit_price)
        self.assertIsNone(combo.default_qty)

        whopper = next((current_order_item for current_order_item in call_args[0][1] if current_order_item.part_code == "1050"), None)  # type: CurrentOrderItem
        self.assertIsNotNone(whopper)
        self.assertEqual(whopper.order_id, 1)
        self.assertEqual(whopper.line_number, 1)
        self.assertEqual(whopper.item_id, "1.1051")
        self.assertEqual(whopper.level, 1)
        self.assertEqual(whopper.part_code, "1050")
        self.assertEqual(whopper.ordered_quantity, 1)
        self.assertIsNone(whopper.last_ordered_quantity)
        self.assertEqual(whopper.included_quantity, 1)
        self.assertEqual(whopper.decremented_quantity, 0)
        self.assertEqual(whopper.price_key, "1050_price_key")
        self.assertEqual(whopper.discount_ammount, 0.0)
        self.assertEqual(whopper.surcharge_ammount, 0.0)
        self.assertEqual(whopper.only_flag, 0)
        self.assertIsNone(whopper.overwrittern_unit_price)
        self.assertEqual(whopper.default_qty, 1)

        ingredients = next((current_order_item for current_order_item in call_args[0][1] if current_order_item.part_code == "8200000"), None)  # type: CurrentOrderItem
        self.assertIsNotNone(ingredients)
        self.assertEqual(ingredients.order_id, 1)
        self.assertEqual(ingredients.line_number, 1)
        self.assertEqual(ingredients.item_id, "1.1051.1050")
        self.assertEqual(ingredients.level, 2)
        self.assertEqual(ingredients.part_code, "8200000")
        self.assertIsNone(ingredients.ordered_quantity)
        self.assertIsNone(ingredients.last_ordered_quantity)
        self.assertEqual(ingredients.included_quantity, 0)
        self.assertEqual(ingredients.decremented_quantity, 0)
        self.assertIsNone(ingredients.price_key)
        self.assertEqual(ingredients.discount_ammount, 0.0)
        self.assertEqual(ingredients.surcharge_ammount, 0.0)
        self.assertEqual(ingredients.only_flag, 0)
        self.assertIsNone(ingredients.overwrittern_unit_price)
        self.assertEqual(ingredients.default_qty, 0)

        extra_maionese = next((current_order_item for current_order_item in call_args[0][1] if current_order_item.part_code == "27001"), None)  # type: CurrentOrderItem
        self.assertIsNotNone(extra_maionese)
        self.assertEqual(extra_maionese.order_id, 1)
        self.assertEqual(extra_maionese.line_number, 1)
        self.assertEqual(extra_maionese.item_id, "1.1051.1050.8200000")
        self.assertEqual(extra_maionese.level, 3)
        self.assertEqual(extra_maionese.part_code, "27001")
        self.assertEqual(extra_maionese.ordered_quantity, 1)
        self.assertIsNone(extra_maionese.last_ordered_quantity)
        self.assertEqual(extra_maionese.included_quantity, 1)
        self.assertEqual(extra_maionese.decremented_quantity, 0)
        self.assertEqual(extra_maionese.price_key, "27001_price_key")
        self.assertEqual(extra_maionese.discount_ammount, 0.0)
        self.assertEqual(extra_maionese.surcharge_ammount, 0.0)
        self.assertEqual(extra_maionese.only_flag, 0)
        self.assertIsNone(extra_maionese.overwrittern_unit_price)
        self.assertEqual(extra_maionese.default_qty, 0)

    def test_ComboWithProductWithOptionWithRemovedDefaultIngredient_OrderRepositoryCalledWithEachLine(self):
        remote_order = RemoteOrder()
        remote_order.pickup = PickUpInfo()
        remote_order.pickup.company = ""

        combo_whopper_tree = CompositionTree()
        combo_whopper_tree.product = ProductNode(part_code="1051", type=CompositionType.COMBO, default_qty=None, current_qty=1, min_qty=None, max_qty=None)
        combo_whopper_tree.sons = []

        whopper_tree = CompositionTree()
        whopper_tree.product = ProductNode(part_code="1050", type=CompositionType.PRODUCT, default_qty=1, current_qty=1, min_qty=1, max_qty=1)
        whopper_tree.sons = []
        whopper_tree.parent = combo_whopper_tree
        combo_whopper_tree.sons.append(whopper_tree)

        ingredients_tree = CompositionTree()
        ingredients_tree.product = ProductNode(part_code="8200000", type=CompositionType.OPTION, default_qty=0, current_qty=1, min_qty=0, max_qty=99)
        ingredients_tree.sons = []
        ingredients_tree.parent = whopper_tree
        whopper_tree.sons.append(ingredients_tree)

        extra_maionese_tree = CompositionTree()
        extra_maionese_tree.product = ProductNode(part_code="27001", type=CompositionType.PRODUCT, default_qty=1, current_qty=0, min_qty=0, max_qty=9)
        extra_maionese_tree.sons = []
        extra_maionese_tree.parent = ingredients_tree
        ingredients_tree.sons.append(extra_maionese_tree)

        self.remote_order_item_creator.create_current_order_items(1, 1, [combo_whopper_tree])
        call_args = self.order_repository.insert_current_order_item.call_args

        self.assertEqual(call_args[0][0], 1)

        combo = next((current_order_item for current_order_item in call_args[0][1] if current_order_item.part_code == "1051"), None)  # type: CurrentOrderItem
        self.assertIsNotNone(combo)
        self.assertEqual(combo.order_id, 1)
        self.assertEqual(combo.line_number, 1)
        self.assertEqual(combo.item_id, "1")
        self.assertEqual(combo.level, 0)
        self.assertEqual(combo.part_code, "1051")
        self.assertEqual(combo.ordered_quantity, 1)
        self.assertIsNone(combo.last_ordered_quantity)
        self.assertEqual(combo.included_quantity, 0)
        self.assertEqual(combo.decremented_quantity, 0)
        self.assertIsNone(combo.price_key)
        self.assertEqual(combo.discount_ammount, 0.0)
        self.assertEqual(combo.surcharge_ammount, 0.0)
        self.assertEqual(combo.only_flag, 0)
        self.assertIsNone(combo.overwrittern_unit_price)
        self.assertIsNone(combo.default_qty)

        whopper = next((current_order_item for current_order_item in call_args[0][1] if current_order_item.part_code == "1050"), None)  # type: CurrentOrderItem
        self.assertIsNotNone(whopper)
        self.assertEqual(whopper.order_id, 1)
        self.assertEqual(whopper.line_number, 1)
        self.assertEqual(whopper.item_id, "1.1051")
        self.assertEqual(whopper.level, 1)
        self.assertEqual(whopper.part_code, "1050")
        self.assertEqual(whopper.ordered_quantity, 1)
        self.assertIsNone(whopper.last_ordered_quantity)
        self.assertEqual(whopper.included_quantity, 1)
        self.assertEqual(whopper.decremented_quantity, 0)
        self.assertEqual(whopper.price_key, "1050_price_key")
        self.assertEqual(whopper.discount_ammount, 0.0)
        self.assertEqual(whopper.surcharge_ammount, 0.0)
        self.assertEqual(whopper.only_flag, 0)
        self.assertIsNone(whopper.overwrittern_unit_price)
        self.assertEqual(whopper.default_qty, 1)

        ingredients = next((current_order_item for current_order_item in call_args[0][1] if current_order_item.part_code == "8200000"), None)  # type: CurrentOrderItem
        self.assertIsNotNone(ingredients)
        self.assertEqual(ingredients.order_id, 1)
        self.assertEqual(ingredients.line_number, 1)
        self.assertEqual(ingredients.item_id, "1.1051.1050")
        self.assertEqual(ingredients.level, 2)
        self.assertEqual(ingredients.part_code, "8200000")
        self.assertIsNone(ingredients.ordered_quantity)
        self.assertIsNone(ingredients.last_ordered_quantity)
        self.assertEqual(ingredients.included_quantity, 0)
        self.assertEqual(ingredients.decremented_quantity, 0)
        self.assertIsNone(ingredients.price_key)
        self.assertEqual(ingredients.discount_ammount, 0.0)
        self.assertEqual(ingredients.surcharge_ammount, 0.0)
        self.assertEqual(ingredients.only_flag, 0)
        self.assertIsNone(ingredients.overwrittern_unit_price)
        self.assertEqual(ingredients.default_qty, 0)

        removed_maionese = next((current_order_item for current_order_item in call_args[0][1] if current_order_item.part_code == "27001"), None)  # type: CurrentOrderItem
        self.assertIsNotNone(removed_maionese)
        self.assertEqual(removed_maionese.order_id, 1)
        self.assertEqual(removed_maionese.line_number, 1)
        self.assertEqual(removed_maionese.item_id, "1.1051.1050.8200000")
        self.assertEqual(removed_maionese.level, 3)
        self.assertEqual(removed_maionese.part_code, "27001")
        self.assertEqual(removed_maionese.ordered_quantity, 0)
        self.assertIsNone(removed_maionese.last_ordered_quantity)
        self.assertEqual(removed_maionese.included_quantity, 0)
        self.assertEqual(removed_maionese.decremented_quantity, 1)
        self.assertEqual(removed_maionese.price_key, "27001_price_key")
        self.assertEqual(removed_maionese.discount_ammount, 0.0)
        self.assertEqual(removed_maionese.surcharge_ammount, 0.0)
        self.assertEqual(removed_maionese.only_flag, 0)
        self.assertIsNone(removed_maionese.overwrittern_unit_price)
        self.assertEqual(removed_maionese.default_qty, 1)

    def test_ComboWithOptionWithProduct_OrderRepositoryCalledWithEachLine(self):
        remote_order = RemoteOrder()
        remote_order.pickup = PickUpInfo()
        remote_order.pickup.company = ""

        combo_whopper_tree = CompositionTree()
        combo_whopper_tree.product = ProductNode(part_code="1051", type=CompositionType.COMBO, default_qty=None, current_qty=1, min_qty=None, max_qty=None)
        combo_whopper_tree.sons = []

        fries_option_tree = CompositionTree()
        fries_option_tree.product = ProductNode(part_code="7300000", type=CompositionType.OPTION, default_qty=0, current_qty=1, min_qty=1, max_qty=1)
        fries_option_tree.sons = []
        fries_option_tree.parent = combo_whopper_tree
        combo_whopper_tree.sons.append(fries_option_tree)

        medium_fries_tree = CompositionTree()
        medium_fries_tree.product = ProductNode(part_code="6012", type=CompositionType.PRODUCT, default_qty=0, current_qty=1, min_qty=0, max_qty=1)
        medium_fries_tree.sons = []
        medium_fries_tree.parent = fries_option_tree
        fries_option_tree.sons.append(medium_fries_tree)

        self.remote_order_item_creator.create_current_order_items(1, 1, [combo_whopper_tree])
        call_args = self.order_repository.insert_current_order_item.call_args

        self.assertEqual(call_args[0][0], 1)

        combo = next((current_order_item for current_order_item in call_args[0][1] if current_order_item.part_code == "1051"), None)  # type: CurrentOrderItem
        self.assertIsNotNone(combo)
        self.assertEqual(combo.order_id, 1)
        self.assertEqual(combo.line_number, 1)
        self.assertEqual(combo.item_id, "1")
        self.assertEqual(combo.level, 0)
        self.assertEqual(combo.part_code, "1051")
        self.assertEqual(combo.ordered_quantity, 1)
        self.assertIsNone(combo.last_ordered_quantity)
        self.assertEqual(combo.included_quantity, 0)
        self.assertEqual(combo.decremented_quantity, 0)
        self.assertIsNone(combo.price_key)
        self.assertEqual(combo.discount_ammount, 0.0)
        self.assertEqual(combo.surcharge_ammount, 0.0)
        self.assertEqual(combo.only_flag, 0)
        self.assertIsNone(combo.overwrittern_unit_price)
        self.assertIsNone(combo.default_qty)

        fries_option = next((current_order_item for current_order_item in call_args[0][1] if current_order_item.part_code == "7300000"), None)  # type: CurrentOrderItem
        self.assertIsNotNone(fries_option)
        self.assertEqual(fries_option.order_id, 1)
        self.assertEqual(fries_option.line_number, 1)
        self.assertEqual(fries_option.item_id, "1.1051")
        self.assertEqual(fries_option.level, 1)
        self.assertEqual(fries_option.part_code, "7300000")
        self.assertIsNone(fries_option.ordered_quantity)
        self.assertIsNone(fries_option.last_ordered_quantity)
        self.assertEqual(fries_option.included_quantity, 1)
        self.assertEqual(fries_option.decremented_quantity, 0)
        self.assertIsNone(fries_option.price_key)
        self.assertEqual(fries_option.discount_ammount, 0.0)
        self.assertEqual(fries_option.surcharge_ammount, 0.0)
        self.assertEqual(fries_option.only_flag, 0)
        self.assertIsNone(fries_option.overwrittern_unit_price)
        self.assertEqual(fries_option.default_qty, 1)

        medium_fries_option = next((current_order_item for current_order_item in call_args[0][1] if current_order_item.part_code == "6012"), None)  # type: CurrentOrderItem
        self.assertIsNotNone(medium_fries_option)
        self.assertEqual(medium_fries_option.order_id, 1)
        self.assertEqual(medium_fries_option.line_number, 1)
        self.assertEqual(medium_fries_option.item_id, "1.1051.7300000")
        self.assertEqual(medium_fries_option.level, 2)
        self.assertEqual(medium_fries_option.part_code, "6012")
        self.assertEqual(medium_fries_option.ordered_quantity, 1)
        self.assertIsNone(medium_fries_option.last_ordered_quantity)
        self.assertEqual(medium_fries_option.included_quantity, 1)
        self.assertEqual(medium_fries_option.decremented_quantity, 0)
        self.assertEqual(medium_fries_option.price_key, "6012_price_key")
        self.assertEqual(medium_fries_option.discount_ammount, 0.0)
        self.assertEqual(medium_fries_option.surcharge_ammount, 0.0)
        self.assertEqual(medium_fries_option.only_flag, 0)
        self.assertIsNone(medium_fries_option.overwrittern_unit_price)
        self.assertEqual(medium_fries_option.default_qty, 0)

    def test_CompleteCombo_OrderRepositoryCalledWithEachLine(self):
        remote_order = RemoteOrder()
        remote_order.pickup = PickUpInfo()
        remote_order.pickup.company = ""

        combo_whopper_tree = CompositionTree()
        combo_whopper_tree.product = ProductNode(part_code="1051", type=CompositionType.COMBO, default_qty=None, current_qty=1, min_qty=None, max_qty=None)
        combo_whopper_tree.sons = []

        whopper_tree = CompositionTree()
        whopper_tree.product = ProductNode(part_code="1050", type=CompositionType.PRODUCT, default_qty=1, current_qty=1, min_qty=1, max_qty=1)
        whopper_tree.sons = []
        whopper_tree.parent = combo_whopper_tree
        combo_whopper_tree.sons.append(whopper_tree)

        ingredients_tree = CompositionTree()
        ingredients_tree.product = ProductNode(part_code="8200000", type=CompositionType.OPTION, default_qty=0, current_qty=1, min_qty=0, max_qty=1)
        ingredients_tree.sons = []
        ingredients_tree.parent = whopper_tree
        whopper_tree.sons.append(ingredients_tree)

        extra_maionese_tree = CompositionTree()
        extra_maionese_tree.product = ProductNode(part_code="27001", type=CompositionType.PRODUCT, default_qty=0, current_qty=1, min_qty=0, max_qty=9)
        extra_maionese_tree.sons = []
        extra_maionese_tree.parent = ingredients_tree
        ingredients_tree.sons.append(extra_maionese_tree)

        fries_option_tree = CompositionTree()
        fries_option_tree.product = ProductNode(part_code="7300000", type=CompositionType.OPTION, default_qty=0, current_qty=1, min_qty=1, max_qty=1)
        fries_option_tree.sons = []
        fries_option_tree.parent = combo_whopper_tree
        combo_whopper_tree.sons.append(fries_option_tree)

        medium_fries_tree = CompositionTree()
        medium_fries_tree.product = ProductNode(part_code="6012", type=CompositionType.PRODUCT, default_qty=0, current_qty=1, min_qty=0, max_qty=1)
        medium_fries_tree.sons = []
        medium_fries_tree.parent = fries_option_tree
        fries_option_tree.sons.append(medium_fries_tree)

        drinks_option_tree = CompositionTree()
        drinks_option_tree.product = ProductNode(part_code="7500000", type=CompositionType.OPTION, default_qty=0, current_qty=1, min_qty=1, max_qty=1)
        drinks_option_tree.sons = []
        drinks_option_tree.parent = combo_whopper_tree
        combo_whopper_tree.sons.append(drinks_option_tree)

        free_refil_tree = CompositionTree()
        free_refil_tree.product = ProductNode(part_code="9008", type=CompositionType.PRODUCT, default_qty=0, current_qty=1, min_qty=0, max_qty=1)
        free_refil_tree.sons = []
        free_refil_tree.parent = drinks_option_tree
        drinks_option_tree.sons.append(free_refil_tree)

        chicken_fries_tree = CompositionTree()
        chicken_fries_tree.product = ProductNode(part_code="9900000", type=CompositionType.OPTION, default_qty=0, current_qty=1, min_qty=0, max_qty=1)
        chicken_fries_tree.sons = []
        chicken_fries_tree.parent = combo_whopper_tree
        combo_whopper_tree.sons.append(chicken_fries_tree)

        self.remote_order_item_creator.create_current_order_items(1, 1, [combo_whopper_tree])
        call_args = self.order_repository.insert_current_order_item.call_args

        self.assertEqual(call_args[0][0], 1)

        combo = next((current_order_item for current_order_item in call_args[0][1] if current_order_item.part_code == "1051"), None)  # type: CurrentOrderItem
        self.assertIsNotNone(combo)
        self.assertEqual(combo.order_id, 1)
        self.assertEqual(combo.line_number, 1)
        self.assertEqual(combo.item_id, "1")
        self.assertEqual(combo.level, 0)
        self.assertEqual(combo.part_code, "1051")
        self.assertEqual(combo.ordered_quantity, 1)
        self.assertIsNone(combo.last_ordered_quantity)
        self.assertEqual(combo.included_quantity, 0)
        self.assertEqual(combo.decremented_quantity, 0)
        self.assertIsNone(combo.price_key)
        self.assertEqual(combo.discount_ammount, 0.0)
        self.assertEqual(combo.surcharge_ammount, 0.0)
        self.assertEqual(combo.only_flag, 0)
        self.assertIsNone(combo.overwrittern_unit_price)
        self.assertIsNone(combo.default_qty)

        whopper = next((current_order_item for current_order_item in call_args[0][1] if current_order_item.part_code == "1050"), None)  # type: CurrentOrderItem
        self.assertIsNotNone(whopper)
        self.assertEqual(whopper.order_id, 1)
        self.assertEqual(whopper.line_number, 1)
        self.assertEqual(whopper.item_id, "1.1051")
        self.assertEqual(whopper.level, 1)
        self.assertEqual(whopper.part_code, "1050")
        self.assertEqual(whopper.ordered_quantity, 1)
        self.assertIsNone(whopper.last_ordered_quantity)
        self.assertEqual(whopper.included_quantity, 1)
        self.assertEqual(whopper.decremented_quantity, 0)
        self.assertEqual(whopper.price_key, "1050_price_key")
        self.assertEqual(whopper.discount_ammount, 0.0)
        self.assertEqual(whopper.surcharge_ammount, 0.0)
        self.assertEqual(whopper.only_flag, 0)
        self.assertIsNone(whopper.overwrittern_unit_price)
        self.assertEqual(whopper.default_qty, 1)

        ingredients = next((current_order_item for current_order_item in call_args[0][1] if current_order_item.part_code == "8200000"), None)  # type: CurrentOrderItem
        self.assertIsNotNone(ingredients)
        self.assertEqual(ingredients.order_id, 1)
        self.assertEqual(ingredients.line_number, 1)
        self.assertEqual(ingredients.item_id, "1.1051.1050")
        self.assertEqual(ingredients.level, 2)
        self.assertEqual(ingredients.part_code, "8200000")
        self.assertIsNone(ingredients.ordered_quantity)
        self.assertIsNone(ingredients.last_ordered_quantity)
        self.assertEqual(ingredients.included_quantity, 0)
        self.assertEqual(ingredients.decremented_quantity, 0)
        self.assertIsNone(ingredients.price_key)
        self.assertEqual(ingredients.discount_ammount, 0.0)
        self.assertEqual(ingredients.surcharge_ammount, 0.0)
        self.assertEqual(ingredients.only_flag, 0)
        self.assertIsNone(ingredients.overwrittern_unit_price)
        self.assertEqual(ingredients.default_qty, 0)

        extra_maionese = next((current_order_item for current_order_item in call_args[0][1] if current_order_item.part_code == "27001"), None)  # type: CurrentOrderItem
        self.assertIsNotNone(extra_maionese)
        self.assertEqual(extra_maionese.order_id, 1)
        self.assertEqual(extra_maionese.line_number, 1)
        self.assertEqual(extra_maionese.item_id, "1.1051.1050.8200000")
        self.assertEqual(extra_maionese.level, 3)
        self.assertEqual(extra_maionese.part_code, "27001")
        self.assertEqual(extra_maionese.ordered_quantity, 1)
        self.assertIsNone(extra_maionese.last_ordered_quantity)
        self.assertEqual(extra_maionese.included_quantity, 1)
        self.assertEqual(extra_maionese.decremented_quantity, 0)
        self.assertEqual(extra_maionese.price_key, "27001_price_key")
        self.assertEqual(extra_maionese.discount_ammount, 0.0)
        self.assertEqual(extra_maionese.surcharge_ammount, 0.0)
        self.assertEqual(extra_maionese.only_flag, 0)
        self.assertIsNone(extra_maionese.overwrittern_unit_price)
        self.assertEqual(extra_maionese.default_qty, 0)

        fries_option = next((current_order_item for current_order_item in call_args[0][1] if current_order_item.part_code == "7300000"), None)  # type: CurrentOrderItem
        self.assertIsNotNone(fries_option)
        self.assertEqual(fries_option.order_id, 1)
        self.assertEqual(fries_option.line_number, 1)
        self.assertEqual(fries_option.item_id, "1.1051")
        self.assertEqual(fries_option.level, 1)
        self.assertEqual(fries_option.part_code, "7300000")
        self.assertIsNone(fries_option.ordered_quantity)
        self.assertIsNone(fries_option.last_ordered_quantity)
        self.assertEqual(fries_option.included_quantity, 1)
        self.assertEqual(fries_option.decremented_quantity, 0)
        self.assertIsNone(fries_option.price_key)
        self.assertEqual(fries_option.discount_ammount, 0.0)
        self.assertEqual(fries_option.surcharge_ammount, 0.0)
        self.assertEqual(fries_option.only_flag, 0)
        self.assertIsNone(fries_option.overwrittern_unit_price)
        self.assertEqual(fries_option.default_qty, 1)

        medium_fries_option = next((current_order_item for current_order_item in call_args[0][1] if current_order_item.part_code == "6012"), None)  # type: CurrentOrderItem
        self.assertIsNotNone(medium_fries_option)
        self.assertEqual(medium_fries_option.order_id, 1)
        self.assertEqual(medium_fries_option.line_number, 1)
        self.assertEqual(medium_fries_option.item_id, "1.1051.7300000")
        self.assertEqual(medium_fries_option.level, 2)
        self.assertEqual(medium_fries_option.part_code, "6012")
        self.assertEqual(medium_fries_option.ordered_quantity, 1)
        self.assertIsNone(medium_fries_option.last_ordered_quantity)
        self.assertEqual(medium_fries_option.included_quantity, 1)
        self.assertEqual(medium_fries_option.decremented_quantity, 0)
        self.assertEqual(medium_fries_option.price_key, "6012_price_key")
        self.assertEqual(medium_fries_option.discount_ammount, 0.0)
        self.assertEqual(medium_fries_option.surcharge_ammount, 0.0)
        self.assertEqual(medium_fries_option.only_flag, 0)
        self.assertIsNone(medium_fries_option.overwrittern_unit_price)
        self.assertEqual(medium_fries_option.default_qty, 0)

        drinks_option = next((current_order_item for current_order_item in call_args[0][1] if current_order_item.part_code == "7500000"), None)  # type: CurrentOrderItem
        self.assertIsNotNone(drinks_option)
        self.assertEqual(drinks_option.order_id, 1)
        self.assertEqual(drinks_option.line_number, 1)
        self.assertEqual(drinks_option.item_id, "1.1051")
        self.assertEqual(drinks_option.level, 1)
        self.assertEqual(drinks_option.part_code, "7500000")
        self.assertIsNone(drinks_option.ordered_quantity)
        self.assertIsNone(drinks_option.last_ordered_quantity)
        self.assertEqual(drinks_option.included_quantity, 1)
        self.assertEqual(drinks_option.decremented_quantity, 0)
        self.assertIsNone(drinks_option.price_key)
        self.assertEqual(drinks_option.discount_ammount, 0.0)
        self.assertEqual(drinks_option.surcharge_ammount, 0.0)
        self.assertEqual(drinks_option.only_flag, 0)
        self.assertIsNone(drinks_option.overwrittern_unit_price)
        self.assertEqual(drinks_option.default_qty, 1)

        free_refil = next((current_order_item for current_order_item in call_args[0][1] if current_order_item.part_code == "9008"), None)  # type: CurrentOrderItem
        self.assertIsNotNone(free_refil)
        self.assertEqual(free_refil.order_id, 1)
        self.assertEqual(free_refil.line_number, 1)
        self.assertEqual(free_refil.item_id, "1.1051.7500000")
        self.assertEqual(free_refil.level, 2)
        self.assertEqual(free_refil.part_code, "9008")
        self.assertEqual(free_refil.ordered_quantity, 1)
        self.assertIsNone(free_refil.last_ordered_quantity)
        self.assertEqual(free_refil.included_quantity, 1)
        self.assertEqual(free_refil.decremented_quantity, 0)
        self.assertEqual(free_refil.price_key, "9008_price_key")
        self.assertEqual(free_refil.discount_ammount, 0.0)
        self.assertEqual(free_refil.surcharge_ammount, 0.0)
        self.assertEqual(free_refil.only_flag, 0)
        self.assertIsNone(free_refil.overwrittern_unit_price)
        self.assertEqual(free_refil.default_qty, 0)

        checkin_fries = next((current_order_item for current_order_item in call_args[0][1] if current_order_item.part_code == "9900000"), None)  # type: CurrentOrderItem
        self.assertIsNotNone(checkin_fries)
        self.assertEqual(checkin_fries.order_id, 1)
        self.assertEqual(checkin_fries.line_number, 1)
        self.assertEqual(checkin_fries.item_id, "1.1051")
        self.assertEqual(checkin_fries.level, 1)
        self.assertEqual(checkin_fries.part_code, "9900000")
        self.assertIsNone(checkin_fries.ordered_quantity)
        self.assertIsNone(checkin_fries.last_ordered_quantity)
        self.assertEqual(checkin_fries.included_quantity, 1)
        self.assertEqual(checkin_fries.decremented_quantity, 0)
        self.assertIsNone(checkin_fries.price_key)
        self.assertEqual(checkin_fries.discount_ammount, 0.0)
        self.assertEqual(checkin_fries.surcharge_ammount, 0.0)
        self.assertEqual(checkin_fries.only_flag, 0)
        self.assertIsNone(checkin_fries.overwrittern_unit_price)
        self.assertEqual(checkin_fries.default_qty, 0)

    def _fake_get_price_key(self, item_id, part_code):
        return part_code + "_price_key"