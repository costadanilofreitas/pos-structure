import unittest
from remoteorder.model import OrderItem
from remoteorder.compositiontree import CompositionTree, ProductNode, CompositionType
from remoteorder import CompositionTreeValidator, OrderValidationException, OrderValidationError


# TODO: Testar caso de produto faltando (Cliente manda ingrediente mas nao manda lanche)
class ValidateOrderCompositionTestCase(unittest.TestCase):
    def test_DirectSon_CompositionValidated(self):
        combo_whopper = CompositionTree()
        combo_whopper.product = ProductNode(
            part_code="1051",
            type=CompositionType.COMBO,
            default_qty=None,
            min_qty=None,
            max_qty=None,
            current_qty=None
        )
        combo_whopper.sons = []

        whopper = CompositionTree()
        whopper.product = ProductNode(
            part_code="1050",
            type=CompositionType.PRODUCT,
            default_qty=1,
            min_qty=1,
            max_qty=1,
            current_qty=None
        )

        combo_whopper.sons.append(whopper)

        order_item = OrderItem()
        order_item.part_code = "1051"
        order_item.quantity = 1
        order_item.parts = []

        son_order_item = OrderItem()
        son_order_item.part_code = "1050"
        son_order_item.quantity = 1
        son_order_item.parts = None

        order_item.parts.append(son_order_item)

        composition_tree_validator = CompositionTreeValidator()

        complete_order = composition_tree_validator.validate_order_composition(combo_whopper, order_item)

        self.assertIsNotNone(complete_order)
        self.assertIsNone(complete_order.parent)
        self.assertIsNotNone(complete_order.product)
        self.assertEqual(complete_order.product.part_code, "1051")
        self.assertEqual(complete_order.product.current_qty, 1)
        self.assertEqual(complete_order.product.type, CompositionType.COMBO)
        self.assertIsNotNone(complete_order.sons)
        self.assertEqual(len(complete_order.sons), 1)

        complete_whopper = complete_order.sons[0]
        self.assertIsNotNone(complete_whopper)
        self.assertEqual(complete_whopper.parent, complete_order)
        self.assertIsNotNone(complete_whopper.product)
        self.assertEqual(complete_whopper.product.part_code, "1050")
        self.assertEqual(complete_whopper.product.current_qty, 1)
        self.assertEqual(complete_whopper.product.type, CompositionType.PRODUCT)
        self.assertIsNotNone(complete_whopper.sons)
        self.assertEqual(len(complete_whopper.sons), 0)

    def test_NoSons_CompositionValidated(self):
        md_fries_tree = CompositionTree()
        md_fries_tree.product = ProductNode(
            part_code="6012",
            type=CompositionType.PRODUCT,
            default_qty=None,
            min_qty=None,
            max_qty=None,
            current_qty=None
        )

        md_fries_item = OrderItem()
        md_fries_item.part_code = "6012"
        md_fries_item.quantity = 2
        md_fries_item.parts = []

        composition_tree_validator = CompositionTreeValidator()
        complete_order = composition_tree_validator.validate_order_composition(md_fries_tree, md_fries_item)

        self.assertIsNotNone(complete_order)
        self.assertIsNone(complete_order.parent)
        self.assertIsNotNone(complete_order.product)
        self.assertEqual(complete_order.product.part_code, "6012")
        self.assertEqual(complete_order.product.current_qty, 2)
        self.assertEqual(complete_order.product.type, CompositionType.PRODUCT)
        self.assertIsNotNone(complete_order.sons)
        self.assertEqual(len(complete_order.sons), 0)

    def test_RootProductNotRootTree_OrderValidationExceptionRaised(self):
        md_fries_tree = CompositionTree()
        md_fries_tree.product = ProductNode(
            part_code="6012",
            type=CompositionType.PRODUCT,
            default_qty=None,
            min_qty=None,
            max_qty=None,
            current_qty=None
        )

        md_fries_item = OrderItem()
        md_fries_item.part_code = "1050"
        md_fries_item.quantity = 1
        md_fries_item.parts = []

        composition_tree_validator = CompositionTreeValidator()
        try:
            composition_tree_validator.validate_order_composition(md_fries_tree, md_fries_item)
            self.fail()
        except OrderValidationException as ex:
            self.assertEqual(ex.order_validation_error, OrderValidationError.InternalError)

    def test_InvalidPartInPartCode_OrderValidationExceptionRaised(self):
        combo_whopper_tree = CompositionTree()
        combo_whopper_tree.product = ProductNode(
            part_code="1051",
            type=CompositionType.COMBO,
            default_qty=None,
            min_qty=None,
            max_qty=None,
            current_qty=None
        )
        combo_whopper_tree.sons = []

        whopper_tree = CompositionTree()
        whopper_tree.product = ProductNode(
            part_code="1050",
            type=CompositionType.PRODUCT,
            default_qty=1,
            min_qty=1,
            max_qty=1,
            current_qty=None
        )

        combo_whopper_tree.sons.append(whopper_tree)

        order_item = OrderItem()
        order_item.part_code = "1051"
        order_item.quantity = 1
        order_item.parts = []

        son_order_item = OrderItem()
        son_order_item.part_code = "1612"
        son_order_item.quantity = 1
        son_order_item.parts = None

        order_item.parts.append(son_order_item)

        composition_tree_validator = CompositionTreeValidator()
        try:
            composition_tree_validator.validate_order_composition(combo_whopper_tree, order_item)
            self.fail()
        except OrderValidationException as ex:
            self.assertEqual(ex.order_validation_error, OrderValidationError.InvalidPartForParentPartCode)

    def test_IndirectSon_CompositionValidated(self):
        combo_whopper_tree = CompositionTree()
        combo_whopper_tree.product = ProductNode(
            part_code="1051",
            type=CompositionType.COMBO,
            default_qty=None,
            min_qty=None,
            max_qty=None,
            current_qty=None
        )
        combo_whopper_tree.sons = []

        drinks_tree = CompositionTree()
        drinks_tree.sons = []
        drinks_tree.product = ProductNode(
            part_code="730000",
            type=CompositionType.OPTION,
            default_qty=0,
            min_qty=2,
            max_qty=2,
            current_qty=None
        )

        combo_whopper_tree.sons.append(drinks_tree)

        free_refil_tree = CompositionTree()
        free_refil_tree.product = ProductNode(
            part_code="9008",
            type=CompositionType.PRODUCT,
            default_qty=2,
            min_qty=0,
            max_qty=2,
            current_qty=None
        )
        drinks_tree.sons.append(free_refil_tree)

        order_item = OrderItem()
        order_item.part_code = "1051"
        order_item.quantity = 1
        order_item.parts = []

        son_order_item = OrderItem()
        son_order_item.part_code = "9008"
        son_order_item.quantity = 2
        son_order_item.parts = None

        order_item.parts.append(son_order_item)

        composition_tree_validator = CompositionTreeValidator()

        complete_order = composition_tree_validator.validate_order_composition(combo_whopper_tree, order_item)

        self.assertIsNotNone(complete_order)
        self.assertIsNone(complete_order.parent)
        self.assertIsNotNone(complete_order.product)
        self.assertEqual(complete_order.product.part_code, "1051")
        self.assertEqual(complete_order.product.current_qty, 1)
        self.assertEqual(complete_order.product.type, CompositionType.COMBO)
        self.assertIsNotNone(complete_order.sons)
        self.assertEqual(len(complete_order.sons), 1)

        drinks_options_tree = complete_order.sons[0]
        self.assertIsNotNone(drinks_options_tree)
        self.assertEqual(drinks_options_tree.parent, complete_order)
        self.assertIsNotNone(drinks_options_tree.product)
        self.assertEqual(drinks_options_tree.product.part_code, "730000")
        self.assertEqual(drinks_options_tree.product.current_qty, 2)
        self.assertEqual(drinks_options_tree.product.type, CompositionType.OPTION)
        self.assertIsNotNone(drinks_options_tree.sons)
        self.assertEqual(len(drinks_options_tree.sons), 1)

        free_refil_tree = drinks_options_tree.sons[0]
        self.assertIsNotNone(free_refil_tree)
        self.assertEqual(free_refil_tree.parent, drinks_options_tree)
        self.assertIsNotNone(free_refil_tree.product)
        self.assertEqual(free_refil_tree.product.part_code, "9008")
        self.assertEqual(free_refil_tree.product.current_qty, 2)
        self.assertEqual(free_refil_tree.product.type, CompositionType.PRODUCT)
        self.assertIsNotNone(free_refil_tree.sons)
        self.assertEqual(len(free_refil_tree.sons), 0)

    def test_MaxQuantityIntermediateExceeded_OrderValidationExceptionRaised(self):
        combo_whopper_tree = CompositionTree()
        combo_whopper_tree.product = ProductNode(
            part_code="1051",
            type=CompositionType.COMBO,
            default_qty=None,
            min_qty=None,
            max_qty=None,
            current_qty=None
        )
        combo_whopper_tree.sons = []

        drinks_tree = CompositionTree()
        drinks_tree.sons = []
        drinks_tree.product = ProductNode(
            part_code="730000",
            type=CompositionType.OPTION,
            default_qty=0,
            min_qty=1,
            max_qty=1,
            current_qty=None
        )

        combo_whopper_tree.sons.append(drinks_tree)

        free_refil_tree = CompositionTree()
        free_refil_tree.product = ProductNode(
            part_code="9008",
            type=CompositionType.PRODUCT,
            default_qty=1,
            min_qty=1,
            max_qty=1,
            current_qty=None
        )

        drinks_tree.sons.append(free_refil_tree)

        order_item = OrderItem()
        order_item.part_code = "1051"
        order_item.quantity = 1
        order_item.parts = []

        son_order_item = OrderItem()
        son_order_item.part_code = "9008"
        son_order_item.quantity = 1
        son_order_item.parts = None

        order_item.parts.append(son_order_item)
        order_item.parts.append(son_order_item)

        composition_tree_validator = CompositionTreeValidator()

        try:
            composition_tree_validator.validate_order_composition(combo_whopper_tree, order_item)
            self.fail()
        except OrderValidationException as ex:
            self.assertEqual(ex.order_validation_error, OrderValidationError.MaxQuantityExceeded)

    def test_MaxQuantityRootExceeded_OrderValidationExceptionRaised(self):
        combo_whopper_tree = CompositionTree()
        combo_whopper_tree.product = ProductNode(
            part_code="1051",
            type=CompositionType.COMBO,
            default_qty=None,
            min_qty=None,
            max_qty=None,
            current_qty=None
        )
        combo_whopper_tree.sons = []

        whopper_tree = CompositionTree()
        whopper_tree.product = ProductNode(
            part_code="1050",
            type=CompositionType.PRODUCT,
            default_qty=1,
            min_qty=1,
            max_qty=1,
            current_qty=None
        )
        whopper_tree.sons = []

        combo_whopper_tree.sons.append(whopper_tree)

        order_item = OrderItem()
        order_item.part_code = "1051"
        order_item.quantity = 1
        order_item.parts = []

        son_order_item = OrderItem()
        son_order_item.part_code = "1050"
        son_order_item.quantity = 1
        son_order_item.parts = None

        order_item.parts.append(son_order_item)
        order_item.parts.append(son_order_item)

        composition_tree_validator = CompositionTreeValidator()

        try:
            composition_tree_validator.validate_order_composition(combo_whopper_tree, order_item)
            self.fail()
        except OrderValidationException as ex:
            self.assertEqual(ex.order_validation_error, OrderValidationError.MaxQuantityExceeded)

    def test_MinQuantityRootNotReached_OrderValidationExceptionRaised(self):
        combo_whopper_tree = CompositionTree()
        combo_whopper_tree.product = ProductNode(
            part_code="1050",
            type=CompositionType.PRODUCT,
            default_qty=None,
            min_qty=None,
            max_qty=None,
            current_qty=None
        )
        combo_whopper_tree.sons = []

        ingredients_tree = CompositionTree()
        ingredients_tree.product = ProductNode(
            part_code="820000",
            type=CompositionType.OPTION,
            default_qty=0,
            min_qty=1,
            max_qty=1,
            current_qty=None
        )
        ingredients_tree.sons = []
        combo_whopper_tree.sons.append(ingredients_tree)

        meat_tree = CompositionTree()
        meat_tree.product = ProductNode(
            part_code="27001",
            type=CompositionType.PRODUCT,
            default_qty=1,
            min_qty=1,
            max_qty=1,
            current_qty=None
        )
        meat_tree.sons = []
        ingredients_tree.sons.append(meat_tree)

        order_item = OrderItem()
        order_item.part_code = "1050"
        order_item.quantity = 1
        order_item.parts = []

        composition_tree_validator = CompositionTreeValidator()

        try:
            composition_tree_validator.validate_order_composition(combo_whopper_tree, order_item)
            self.fail()
        except OrderValidationException as ex:
            self.assertEqual(ex.order_validation_error, OrderValidationError.MinQuantityNotReached)

    def test_MinQuantityIntermediateNotReached_OrderValidationExceptionRaised(self):
        combo_whopper_tree = CompositionTree()
        combo_whopper_tree.product = ProductNode(
            part_code="1051",
            type=CompositionType.COMBO,
            default_qty=None,
            min_qty=None,
            max_qty=None,
            current_qty=None
        )
        combo_whopper_tree.sons = []

        drinks_tree = CompositionTree()
        drinks_tree.sons = []
        drinks_tree.product = ProductNode(
            part_code="730000",
            type=CompositionType.OPTION,
            default_qty=0,
            min_qty=1,
            max_qty=1,
            current_qty=None
        )

        combo_whopper_tree.sons.append(drinks_tree)

        free_refil_tree = CompositionTree()
        free_refil_tree.product = ProductNode(
            part_code="9008",
            type=CompositionType.PRODUCT,
            default_qty=1,
            min_qty=1,
            max_qty=1,
            current_qty=None
        )

        drinks_tree.sons.append(free_refil_tree)

        order_item = OrderItem()
        order_item.part_code = "1051"
        order_item.quantity = 1
        order_item.parts = []

        son_order_item = OrderItem()
        son_order_item.part_code = "9008"
        son_order_item.quantity = 1
        son_order_item.parts = []

        composition_tree_validator = CompositionTreeValidator()
        try:
            composition_tree_validator.validate_order_composition(combo_whopper_tree, order_item)
            self.fail()
        except OrderValidationException as ex:
            self.assertEqual(ex.order_validation_error, OrderValidationError.MinQuantityNotReached)

    def test_TwoPossibleOptionsNonePresent_OrderValidationException(self):
        combo_whopper_tree = CompositionTree()
        combo_whopper_tree.product = ProductNode(
            part_code="1051",
            type=CompositionType.COMBO,
            default_qty=None,
            min_qty=None,
            max_qty=None,
            current_qty=None
        )
        combo_whopper_tree.sons = []

        drinks_tree = CompositionTree()
        drinks_tree.sons = []
        drinks_tree.product = ProductNode(
            part_code="730000",
            type=CompositionType.OPTION,
            default_qty=0,
            min_qty=1,
            max_qty=1,
            current_qty=None
        )
        combo_whopper_tree.sons.append(drinks_tree)

        free_refil_tree = CompositionTree()
        free_refil_tree.sons = []
        free_refil_tree.product = ProductNode(
            part_code="9008",
            type=CompositionType.PRODUCT,
            default_qty=1,
            min_qty=0,
            max_qty=1,
            current_qty=None
        )
        drinks_tree.sons.append(free_refil_tree)

        juice_tree = CompositionTree()
        juice_tree.sons = []
        juice_tree.product = ProductNode(
            part_code="9009",
            type=CompositionType.PRODUCT,
            default_qty=0,
            min_qty=0,
            max_qty=1,
            current_qty=None
        )
        drinks_tree.sons.append(juice_tree)

        order_item = OrderItem()
        order_item.part_code = "1051"
        order_item.quantity = 1
        order_item.parts = []

        composition_tree_validator = CompositionTreeValidator()
        try:
            composition_tree_validator.validate_order_composition(combo_whopper_tree, order_item)
            self.fail()
        except OrderValidationException as ex:
            self.assertEqual(ex.order_validation_error, OrderValidationError.MinQuantityNotReached)

    def test_CompleteCombo_CompositionValidated(self):
        combo_whopper_tree = CompositionTree()
        combo_whopper_tree.product = ProductNode(
            part_code="1051",
            type=CompositionType.COMBO,
            default_qty=None,
            min_qty=None,
            max_qty=None,
            current_qty=None
        )
        combo_whopper_tree.sons = []

        whopper_tree = CompositionTree()
        whopper_tree.product = ProductNode(
            part_code="1050",
            type=CompositionType.PRODUCT,
            default_qty=1,
            min_qty=1,
            max_qty=1,
            current_qty=None
        )
        whopper_tree.sons = []
        combo_whopper_tree.sons.append(whopper_tree)

        drinks_tree = CompositionTree()
        drinks_tree.sons = []
        drinks_tree.product = ProductNode(
            part_code="730000",
            type=CompositionType.OPTION,
            default_qty=0,
            min_qty=1,
            max_qty=1,
            current_qty=None
        )
        combo_whopper_tree.sons.append(drinks_tree)

        free_refil_tree = CompositionTree()
        free_refil_tree.sons = []
        free_refil_tree.product = ProductNode(
            part_code="9008",
            type=CompositionType.PRODUCT,
            default_qty=1,
            min_qty=0,
            max_qty=1,
            current_qty=None
        )
        drinks_tree.sons.append(free_refil_tree)

        juice_tree = CompositionTree()
        juice_tree.sons = []
        juice_tree.product = ProductNode(
            part_code="9009",
            type=CompositionType.PRODUCT,
            default_qty=0,
            min_qty=0,
            max_qty=1,
            current_qty=None
        )
        drinks_tree.sons.append(juice_tree)

        fries_tree = CompositionTree()
        fries_tree.sons = []
        fries_tree.product = ProductNode(
            part_code="750000",
            type=CompositionType.OPTION,
            default_qty=0,
            min_qty=1,
            max_qty=1,
            current_qty=None
        )
        combo_whopper_tree.sons.append(fries_tree)

        small_fries = CompositionTree()
        small_fries.sons = []
        small_fries.product = ProductNode(
            part_code="6012",
            type=CompositionType.PRODUCT,
            default_qty=1,
            min_qty=0,
            max_qty=1,
            current_qty=None
        )
        fries_tree.sons.append(small_fries)

        large_fries = CompositionTree()
        large_fries.sons = []
        large_fries.product = ProductNode(
            part_code="6013",
            type=CompositionType.PRODUCT,
            default_qty=0,
            min_qty=0,
            max_qty=1,
            current_qty=None
        )
        fries_tree.sons.append(large_fries)

        combo_item = OrderItem()
        combo_item.part_code = "1051"
        combo_item.quantity = 1
        combo_item.parts = []

        whopper_item = OrderItem()
        whopper_item.part_code = "1050"
        whopper_item.quantity = 1
        whopper_item.parts = []

        large_fries_item = OrderItem()
        large_fries_item.part_code = "6013"
        large_fries_item.quantity = 1
        large_fries_item.parts = []

        free_refil_item = OrderItem()
        free_refil_item.part_code = "9008"
        free_refil_item.quantity = 1
        free_refil_item.parts = []

        combo_item.parts.append(whopper_item)
        combo_item.parts.append(large_fries_item)
        combo_item.parts.append(free_refil_item)

        composition_tree_validator = CompositionTreeValidator()
        new_combo_tree = composition_tree_validator.validate_order_composition(combo_whopper_tree, combo_item)
        self.assertIsNotNone(new_combo_tree)
        self.assertIsNone(new_combo_tree.parent)
        self.assertIsNotNone(new_combo_tree.product)
        self.assertEqual(new_combo_tree.product.part_code, "1051")
        self.assertEqual(new_combo_tree.product.current_qty, 1)
        self.assertEqual(new_combo_tree.product.type, CompositionType.COMBO)
        self.assertIsNotNone(new_combo_tree.sons)
        self.assertEqual(len(new_combo_tree.sons), 3)

        new_whopper_tree = next((son for son in new_combo_tree.sons if son.product.part_code == "1050"), None)
        self.assertIsNotNone(new_whopper_tree)
        self.assertEqual(new_whopper_tree.parent, new_combo_tree)
        self.assertIsNotNone(new_whopper_tree.product)
        self.assertEqual(new_whopper_tree.product.part_code, "1050")
        self.assertEqual(new_whopper_tree.product.current_qty, 1)
        self.assertEqual(new_whopper_tree.product.type, CompositionType.PRODUCT)
        self.assertIsNotNone(new_whopper_tree.sons)
        self.assertEqual(len(new_whopper_tree.sons), 0)

        new_drinks_tree = next((son for son in new_combo_tree.sons if son.product.part_code == "730000"), None)
        self.assertIsNotNone(new_drinks_tree)
        self.assertEqual(new_drinks_tree.parent, new_combo_tree)
        self.assertIsNotNone(new_drinks_tree.product)
        self.assertEqual(new_drinks_tree.product.part_code, "730000")
        self.assertEqual(new_drinks_tree.product.current_qty, 1)
        self.assertEqual(new_drinks_tree.product.type, CompositionType.OPTION)
        self.assertIsNotNone(new_drinks_tree.sons)
        self.assertEqual(len(new_drinks_tree.sons), 1)

        free_refil_tree = new_drinks_tree.sons[0]
        self.assertIsNotNone(free_refil_tree)
        self.assertEqual(free_refil_tree.parent, new_drinks_tree)
        self.assertIsNotNone(free_refil_tree.product)
        self.assertEqual(free_refil_tree.product.part_code, "9008")
        self.assertEqual(free_refil_tree.product.current_qty, 1)
        self.assertEqual(free_refil_tree.product.type, CompositionType.PRODUCT)
        self.assertIsNotNone(free_refil_tree.sons)
        self.assertEqual(len(free_refil_tree.sons), 0)

        new_fries_tree = next((son for son in new_combo_tree.sons if son.product.part_code == "750000"), None)
        self.assertIsNotNone(new_fries_tree)
        self.assertEqual(new_fries_tree.parent, new_combo_tree)
        self.assertIsNotNone(new_fries_tree.product)
        self.assertEqual(new_fries_tree.product.part_code, "750000")
        self.assertEqual(new_fries_tree.product.current_qty, 1)
        self.assertEqual(new_fries_tree.product.type, CompositionType.OPTION)
        self.assertIsNotNone(new_fries_tree.sons)
        self.assertEqual(len(new_fries_tree.sons), 1)

        new_large_fries_tree = new_fries_tree.sons[0]
        self.assertIsNotNone(new_large_fries_tree)
        self.assertEqual(new_large_fries_tree.parent, new_fries_tree)
        self.assertIsNotNone(new_large_fries_tree.product)
        self.assertEqual(new_large_fries_tree.product.part_code, "6013")
        self.assertEqual(new_large_fries_tree.product.current_qty, 1)
        self.assertEqual(new_large_fries_tree.product.type, CompositionType.PRODUCT)
        self.assertIsNotNone(new_large_fries_tree.sons)
        self.assertEqual(len(new_large_fries_tree.sons), 0)

    def test_OptionalOptionNotFilled_CompositionValidated(self):
        whopper_tree = CompositionTree()
        whopper_tree.product = ProductNode(
            part_code="1050",
            type=CompositionType.PRODUCT,
            default_qty=None,
            min_qty=None,
            max_qty=None,
            current_qty=None
        )
        whopper_tree.sons = []

        ingredients_tree = CompositionTree()
        ingredients_tree.product = ProductNode(
            part_code="820000",
            type=CompositionType.OPTION,
            default_qty=0,
            min_qty=0,
            max_qty=10,
            current_qty=None
        )
        ingredients_tree.sons = []
        whopper_tree.sons.append(ingredients_tree)

        ingredient1_tree = CompositionTree()
        ingredient1_tree.sons = []
        ingredient1_tree.product = ProductNode(
            part_code="870001",
            type=CompositionType.PRODUCT,
            default_qty=0,
            min_qty=0,
            max_qty=9,
            current_qty=None
        )
        whopper_tree.sons.append(ingredient1_tree)

        ingredient2_tree = CompositionTree()
        ingredient2_tree.sons = []
        ingredient2_tree.product = ProductNode(
            part_code="870002",
            type=CompositionType.PRODUCT,
            default_qty=0,
            min_qty=0,
            max_qty=9,
            current_qty=None
        )
        whopper_tree.sons.append(ingredient1_tree)

        whopper_item = OrderItem()
        whopper_item.part_code = "1050"
        whopper_item.quantity = 1
        whopper_item.parts = []

        composition_tree_validator = CompositionTreeValidator()
        new_whopper_tree = composition_tree_validator.validate_order_composition(whopper_tree, whopper_item)
        self.assertIsNotNone(new_whopper_tree)
        self.assertIsNone(new_whopper_tree.parent)
        self.assertIsNotNone(new_whopper_tree.product)
        self.assertEqual(new_whopper_tree.product.part_code, "1050")
        self.assertEqual(new_whopper_tree.product.current_qty, 1)
        self.assertEqual(new_whopper_tree.product.type, CompositionType.PRODUCT)
        self.assertIsNotNone(new_whopper_tree.sons)
        self.assertEqual(len(new_whopper_tree.sons), 0)

    def test_DefaultOptionNotFilled_CompositionValidated(self):
        whopper_tree = CompositionTree()
        whopper_tree.product = ProductNode(
            part_code="1050",
            type=CompositionType.PRODUCT,
            default_qty=None,
            min_qty=None,
            max_qty=None,
            current_qty=None
        )
        whopper_tree.sons = []

        ingredients_tree = CompositionTree()
        ingredients_tree.product = ProductNode(
            part_code="820000",
            type=CompositionType.OPTION,
            default_qty=0,
            min_qty=0,
            max_qty=10,
            current_qty=None
        )
        ingredients_tree.sons = []
        whopper_tree.sons.append(ingredients_tree)

        ingredient1_tree = CompositionTree()
        ingredient1_tree.sons = []
        ingredient1_tree.product = ProductNode(
            part_code="870001",
            type=CompositionType.PRODUCT,
            default_qty=1,
            min_qty=0,
            max_qty=9,
            current_qty=None
        )
        whopper_tree.sons.append(ingredient1_tree)

        ingredient2_tree = CompositionTree()
        ingredient2_tree.sons = []
        ingredient2_tree.product = ProductNode(
            part_code="870002",
            type=CompositionType.PRODUCT,
            default_qty=1,
            min_qty=0,
            max_qty=9,
            current_qty=None
        )
        whopper_tree.sons.append(ingredient1_tree)

        whopper_item = OrderItem()
        whopper_item.part_code = "1050"
        whopper_item.quantity = 1
        whopper_item.parts = []

        composition_tree_validator = CompositionTreeValidator()
        new_whopper_tree = composition_tree_validator.validate_order_composition(whopper_tree, whopper_item)
        self.assertIsNotNone(new_whopper_tree)
        self.assertIsNone(new_whopper_tree.parent)
        self.assertIsNotNone(new_whopper_tree.product)
        self.assertEqual(new_whopper_tree.product.part_code, "1050")
        self.assertEqual(new_whopper_tree.product.current_qty, 1)
        self.assertEqual(new_whopper_tree.product.type, CompositionType.PRODUCT)
        self.assertIsNotNone(new_whopper_tree.sons)
        self.assertEqual(len(new_whopper_tree.sons), 0)

    def test_ComboWithoutProduct_CompositionValidated(self):
        combo_whopper_tree = CompositionTree()
        combo_whopper_tree.product = ProductNode(
            part_code="1051",
            type=CompositionType.COMBO,
            default_qty=None,
            min_qty=None,
            max_qty=None,
            current_qty=None
        )
        combo_whopper_tree.sons = []

        whpper_tree = CompositionTree()
        whpper_tree.product = ProductNode(
            part_code="1050",
            type=CompositionType.PRODUCT,
            default_qty=1,
            min_qty=1,
            max_qty=1,
            current_qty=None
        )
        whpper_tree.sons = []
        combo_whopper_tree.sons.append(whpper_tree)

        combo_whopper_item = OrderItem()
        combo_whopper_item.part_code = "1051"
        combo_whopper_item.quantity = 1
        combo_whopper_item.parts = []

        composition_tree_validator = CompositionTreeValidator()
        new_combo_whopper_tree = composition_tree_validator.validate_order_composition(combo_whopper_tree, combo_whopper_item)
        self.assertIsNotNone(new_combo_whopper_tree)
        self.assertIsNone(new_combo_whopper_tree.parent)
        self.assertIsNotNone(new_combo_whopper_tree.product)
        self.assertEqual(new_combo_whopper_tree.product.part_code, "1051")
        self.assertEqual(new_combo_whopper_tree.product.current_qty, 1)
        self.assertEqual(new_combo_whopper_tree.product.type, CompositionType.COMBO)
        self.assertIsNotNone(new_combo_whopper_tree.sons)
        self.assertEqual(len(new_combo_whopper_tree.sons), 1)

        new_whopper_tree = new_combo_whopper_tree.sons[0]
        self.assertIsNotNone(new_whopper_tree)
        self.assertEqual(new_whopper_tree.parent, new_combo_whopper_tree)
        self.assertIsNotNone(new_whopper_tree.product)
        self.assertEqual(new_whopper_tree.product.part_code, "1050")
        self.assertEqual(new_whopper_tree.product.current_qty, 1)
        self.assertEqual(new_whopper_tree.product.type, CompositionType.PRODUCT)
        self.assertIsNotNone(new_whopper_tree.sons)
        self.assertEqual(len(new_whopper_tree.sons), 0)

    def test_SonPartNotInComposition_OrderValidationException(self):
        combo_whopper_tree = CompositionTree()
        combo_whopper_tree.product = ProductNode(
            part_code="1051",
            type=CompositionType.COMBO,
            default_qty=None,
            min_qty=None,
            max_qty=None,
            current_qty=None
        )
        combo_whopper_tree.sons = []

        combo_whopper_item = OrderItem()
        combo_whopper_item.part_code = "1051"
        combo_whopper_item.quantity = 1
        combo_whopper_item.parts = []

        whopper_item = OrderItem()
        whopper_item.part_code = "1050"
        whopper_item.quantity = 1
        whopper_item.parts = []
        combo_whopper_item.parts.append(combo_whopper_item)

        composition_tree_validator = CompositionTreeValidator()
        try:
            composition_tree_validator.validate_order_composition(combo_whopper_tree, combo_whopper_item)
            self.fail()
        except OrderValidationException as ex:
            self.assertEqual(ex.order_validation_error, OrderValidationError.InvalidPartForParentPartCode)

    def test_ProductWithTwoIngredients_IngredientsAndOptionQuantityAreCorrect(self):
        whopper_tree = CompositionTree()
        whopper_tree.product = ProductNode(
            part_code="1050",
            type=CompositionType.PRODUCT,
            default_qty=None,
            min_qty=None,
            max_qty=None,
            current_qty=None
        )
        whopper_tree.sons = []

        ingredients_tree = CompositionTree()
        ingredients_tree.sons = []
        ingredients_tree.product = ProductNode(
            part_code="820000",
            type=CompositionType.OPTION,
            default_qty=0,
            min_qty=1,
            max_qty=99,
            current_qty=None
        )
        whopper_tree.sons.append(ingredients_tree)

        meat_tree = CompositionTree()
        meat_tree.sons = []
        meat_tree.product = ProductNode(
            part_code="27001",
            type=CompositionType.PRODUCT,
            default_qty=0,
            min_qty=0,
            max_qty=9,
            current_qty=None
        )
        ingredients_tree.sons.append(meat_tree)

        maionese_tree = CompositionTree()
        maionese_tree.sons = []
        maionese_tree.product = ProductNode(
            part_code="27002",
            type=CompositionType.PRODUCT,
            default_qty=0,
            min_qty=0,
            max_qty=9,
            current_qty=None
        )
        ingredients_tree.sons.append(maionese_tree)

        whopper_item = OrderItem()
        whopper_item.part_code = "1050"
        whopper_item.quantity = 1
        whopper_item.parts = []

        meat_item = OrderItem()
        meat_item.part_code = "27001"
        meat_item.quantity = 2
        meat_item.parts = []

        maionese_item = OrderItem()
        maionese_item.part_code = "27002"
        maionese_item.quantity = 3
        maionese_item.parts = []

        whopper_item.parts.append(meat_item)
        whopper_item.parts.append(maionese_item)

        composition_tree_validator = CompositionTreeValidator()
        new_whopper_tree = composition_tree_validator.validate_order_composition(whopper_tree, whopper_item)
        self.assertIsNotNone(new_whopper_tree)
        self.assertIsNone(new_whopper_tree.parent)
        self.assertIsNotNone(new_whopper_tree.product)
        self.assertEqual(new_whopper_tree.product.part_code, "1050")
        self.assertEqual(new_whopper_tree.product.current_qty, 1)
        self.assertEqual(new_whopper_tree.product.type, CompositionType.PRODUCT)
        self.assertIsNotNone(new_whopper_tree.sons)
        self.assertEqual(len(new_whopper_tree.sons), 1)

        new_ingredients_tree = next((son for son in new_whopper_tree.sons if son.product.part_code == "820000"), None)
        self.assertIsNotNone(new_ingredients_tree)
        self.assertEqual(new_ingredients_tree.parent, new_whopper_tree)
        self.assertIsNotNone(new_ingredients_tree.product)
        self.assertEqual(new_ingredients_tree.product.part_code, "820000")
        self.assertEqual(new_ingredients_tree.product.current_qty, 5)
        self.assertEqual(new_ingredients_tree.product.type, CompositionType.OPTION)
        self.assertIsNotNone(new_ingredients_tree.sons)
        self.assertEqual(len(new_ingredients_tree.sons), 2)

        new_meat_tree = next((son for son in new_ingredients_tree.sons if son.product.part_code == "27001"), None)
        self.assertIsNotNone(new_meat_tree)
        self.assertEqual(new_meat_tree.parent, new_ingredients_tree)
        self.assertIsNotNone(new_meat_tree.product)
        self.assertEqual(new_meat_tree.product.part_code, "27001")
        self.assertEqual(new_meat_tree.product.current_qty, 2)
        self.assertEqual(new_meat_tree.product.type, CompositionType.PRODUCT)
        self.assertIsNotNone(new_meat_tree.sons)
        self.assertEqual(len(new_meat_tree.sons), 0)

        new_maionese_tree = next((son for son in new_ingredients_tree.sons if son.product.part_code == "27002"), None)
        self.assertIsNotNone(new_maionese_tree)
        self.assertEqual(new_maionese_tree.parent, new_ingredients_tree)
        self.assertIsNotNone(new_maionese_tree.product)
        self.assertEqual(new_maionese_tree.product.part_code, "27002")
        self.assertEqual(new_maionese_tree.product.current_qty, 3)
        self.assertEqual(new_maionese_tree.product.type, CompositionType.PRODUCT)
        self.assertIsNotNone(new_maionese_tree.sons)
        self.assertEqual(len(new_maionese_tree.sons), 0)

    def test_ProductWithTwoRepeatedIngredients_IngredientsAndOptionQuantityAreCorrect(self):
        whopper_tree = CompositionTree()
        whopper_tree.product = ProductNode(
            part_code="1050",
            type=CompositionType.PRODUCT,
            default_qty=None,
            min_qty=None,
            max_qty=None,
            current_qty=None
        )
        whopper_tree.sons = []

        ingredients_tree = CompositionTree()
        ingredients_tree.sons = []
        ingredients_tree.product = ProductNode(
            part_code="820000",
            type=CompositionType.OPTION,
            default_qty=0,
            min_qty=1,
            max_qty=99,
            current_qty=None
        )
        whopper_tree.sons.append(ingredients_tree)

        meat_tree = CompositionTree()
        meat_tree.sons = []
        meat_tree.product = ProductNode(
            part_code="27001",
            type=CompositionType.PRODUCT,
            default_qty=1,
            min_qty=0,
            max_qty=9,
            current_qty=None
        )
        ingredients_tree.sons.append(meat_tree)

        maionese_tree = CompositionTree()
        maionese_tree.sons = []
        maionese_tree.product = ProductNode(
            part_code="27002",
            type=CompositionType.PRODUCT,
            default_qty=1,
            min_qty=0,
            max_qty=9,
            current_qty=None
        )
        ingredients_tree.sons.append(maionese_tree)

        whopper_item = OrderItem()
        whopper_item.part_code = "1050"
        whopper_item.quantity = 1
        whopper_item.parts = []

        meat_item = OrderItem()
        meat_item.part_code = "27001"
        meat_item.quantity = 2
        meat_item.parts = []

        maionese_item = OrderItem()
        maionese_item.part_code = "27001"
        maionese_item.quantity = 3
        maionese_item.parts = []

        whopper_item.parts.append(meat_item)
        whopper_item.parts.append(maionese_item)

        composition_tree_validator = CompositionTreeValidator()
        new_whopper_tree = composition_tree_validator.validate_order_composition(whopper_tree, whopper_item)
        self.assertIsNotNone(new_whopper_tree)
        self.assertIsNone(new_whopper_tree.parent)
        self.assertIsNotNone(new_whopper_tree.product)
        self.assertEqual(new_whopper_tree.product.part_code, "1050")
        self.assertIsNone(new_whopper_tree.product.default_qty)
        self.assertEqual(new_whopper_tree.product.current_qty, 1)
        self.assertEqual(new_whopper_tree.product.type, CompositionType.PRODUCT)
        self.assertIsNotNone(new_whopper_tree.sons)
        self.assertEqual(len(new_whopper_tree.sons), 1)

        new_ingredients_tree = next((son for son in new_whopper_tree.sons if son.product.part_code == "820000"), None)
        self.assertIsNotNone(new_ingredients_tree)
        self.assertEqual(new_ingredients_tree.parent, new_whopper_tree)
        self.assertIsNotNone(new_ingredients_tree.product)
        self.assertEqual(new_ingredients_tree.product.part_code, "820000")
        self.assertEqual(new_ingredients_tree.product.default_qty, 0)
        self.assertEqual(new_ingredients_tree.product.current_qty, 6)
        self.assertEqual(new_ingredients_tree.product.type, CompositionType.OPTION)
        self.assertIsNotNone(new_ingredients_tree.sons)
        self.assertEqual(len(new_ingredients_tree.sons), 1)

        new_meat_tree = next((son for son in new_ingredients_tree.sons if son.product.part_code == "27001"), None)
        self.assertIsNotNone(new_meat_tree)
        self.assertEqual(new_meat_tree.parent, new_ingredients_tree)
        self.assertIsNotNone(new_meat_tree.product)
        self.assertEqual(new_meat_tree.product.part_code, "27001")
        self.assertEqual(new_meat_tree.product.default_qty, 1)
        self.assertEqual(new_meat_tree.product.current_qty, 6)
        self.assertEqual(new_meat_tree.product.type, CompositionType.PRODUCT)
        self.assertIsNotNone(new_meat_tree.sons)
        self.assertEqual(len(new_meat_tree.sons), 0)

    # TODO: implementar este caso
    def ComboWithOptionWithDefaultProductOnlyComboSend_CompositionValidatedWithDefaultProduct(self):
        combo_whopper_tree = CompositionTree()
        combo_whopper_tree.product = ProductNode(
            part_code="1051",
            type=CompositionType.COMBO,
            default_qty=None,
            min_qty=None,
            max_qty=None,
            current_qty=None
        )
        combo_whopper_tree.sons = []

        drinks_tree = CompositionTree()
        drinks_tree.sons = []
        drinks_tree.product = ProductNode(
            part_code="730000",
            type=CompositionType.OPTION,
            default_qty=0,
            min_qty=1,
            max_qty=1,
            current_qty=None
        )
        combo_whopper_tree.sons.append(drinks_tree)

        free_refil_tree = CompositionTree()
        free_refil_tree.sons = []
        free_refil_tree.product = ProductNode(
            part_code="9008",
            type=CompositionType.PRODUCT,
            default_qty=1,
            min_qty=0,
            max_qty=1,
            current_qty=None
        )
        drinks_tree.sons.append(free_refil_tree)

        combo_item = OrderItem()
        combo_item.part_code = "1051"
        combo_item.quantity = 1
        combo_item.parts = []

        composition_tree_validator = CompositionTreeValidator()
        new_combo_tree = composition_tree_validator.validate_order_composition(combo_whopper_tree, combo_item)
        self.assertIsNotNone(new_combo_tree)
        self.assertIsNone(new_combo_tree.parent)
        self.assertIsNotNone(new_combo_tree.product)
        self.assertEqual(new_combo_tree.product.part_code, "1051")
        self.assertEqual(new_combo_tree.product.current_qty, 1)
        self.assertEqual(new_combo_tree.product.type, CompositionType.COMBO)
        self.assertIsNotNone(new_combo_tree.sons)
        self.assertEqual(len(new_combo_tree.sons), 1)

        new_drinks_tree = next((son for son in new_combo_tree.sons if son.product.part_code == "730000"), None)
        self.assertIsNotNone(new_drinks_tree)
        self.assertEqual(new_drinks_tree.parent, new_combo_tree)
        self.assertIsNotNone(new_drinks_tree.product)
        self.assertEqual(new_drinks_tree.product.part_code, "730000")
        self.assertEqual(new_drinks_tree.product.current_qty, 1)
        self.assertEqual(new_drinks_tree.product.type, CompositionType.OPTION)
        self.assertIsNotNone(new_drinks_tree.sons)
        self.assertEqual(len(new_drinks_tree.sons), 1)

        free_refil_tree = new_drinks_tree.sons[0]
        self.assertIsNotNone(free_refil_tree)
        self.assertEqual(free_refil_tree.parent, new_drinks_tree)
        self.assertIsNotNone(free_refil_tree.product)
        self.assertEqual(free_refil_tree.product.part_code, "9008")
        self.assertEqual(free_refil_tree.product.current_qty, 1)
        self.assertEqual(free_refil_tree.product.type, CompositionType.PRODUCT)
        self.assertIsNotNone(free_refil_tree.sons)
        self.assertEqual(len(free_refil_tree.sons), 0)

    def test_ProductWithRemovedDefaultIngredient_CompositionValidatedWithRemovedIngredient(self):
        combo_whopper_tree = CompositionTree()
        combo_whopper_tree.product = ProductNode(
            part_code="1050",
            type=CompositionType.PRODUCT,
            default_qty=None,
            min_qty=None,
            max_qty=None,
            current_qty=None
        )
        combo_whopper_tree.sons = []

        drinks_tree = CompositionTree()
        drinks_tree.sons = []
        drinks_tree.product = ProductNode(
            part_code="820000",
            type=CompositionType.OPTION,
            default_qty=0,
            min_qty=0,
            max_qty=99,
            current_qty=None
        )
        combo_whopper_tree.sons.append(drinks_tree)

        free_refil_tree = CompositionTree()
        free_refil_tree.sons = []
        free_refil_tree.product = ProductNode(
            part_code="27001",
            type=CompositionType.PRODUCT,
            default_qty=1,
            min_qty=0,
            max_qty=9,
            current_qty=None
        )
        drinks_tree.sons.append(free_refil_tree)

        whopper_item = OrderItem()
        whopper_item.part_code = "1050"
        whopper_item.quantity = 1
        whopper_item.parts = []

        free_refil_item = OrderItem()
        free_refil_item.part_code = "27001"
        free_refil_item.quantity = -1
        free_refil_item.parts = []
        whopper_item.parts.append(free_refil_item)

        composition_tree_validator = CompositionTreeValidator()
        new_combo_tree = composition_tree_validator.validate_order_composition(combo_whopper_tree, whopper_item)
        self.assertIsNotNone(new_combo_tree)
        self.assertIsNone(new_combo_tree.parent)
        self.assertIsNotNone(new_combo_tree.product)
        self.assertEqual(new_combo_tree.product.part_code, "1050")
        self.assertIsNone(new_combo_tree.product.default_qty)
        self.assertEqual(new_combo_tree.product.current_qty, 1)
        self.assertEqual(new_combo_tree.product.type, CompositionType.PRODUCT)
        self.assertIsNotNone(new_combo_tree.sons)
        self.assertEqual(len(new_combo_tree.sons), 1)

        new_drinks_tree = next((son for son in new_combo_tree.sons if son.product.part_code == "820000"), None)
        self.assertIsNotNone(new_drinks_tree)
        self.assertEqual(new_drinks_tree.parent, new_combo_tree)
        self.assertIsNotNone(new_drinks_tree.product)
        self.assertEqual(new_drinks_tree.product.part_code, "820000")
        self.assertEqual(new_drinks_tree.product.default_qty, 0)
        self.assertEqual(new_drinks_tree.product.current_qty, 0)
        self.assertEqual(new_drinks_tree.product.type, CompositionType.OPTION)
        self.assertIsNotNone(new_drinks_tree.sons)
        self.assertEqual(len(new_drinks_tree.sons), 1)

        free_refil_tree = new_drinks_tree.sons[0]
        self.assertIsNotNone(free_refil_tree)
        self.assertEqual(free_refil_tree.parent, new_drinks_tree)
        self.assertIsNotNone(free_refil_tree.product)
        self.assertEqual(free_refil_tree.product.part_code, "27001")
        self.assertEqual(free_refil_tree.product.default_qty, 1)
        self.assertEqual(free_refil_tree.product.current_qty, 0)
        self.assertEqual(free_refil_tree.product.type, CompositionType.PRODUCT)
        self.assertIsNotNone(free_refil_tree.sons)
        self.assertEqual(len(free_refil_tree.sons), 0)
