# encoding: utf-8
import unittest
import mock

from remoteorder.compositiontree import CompositionTreeBuilder, CompositionType, ProductRepository, ProductPart, CompositionTreeException, CompositionTreeError


# TODO: Criar teste para combo dentro de combo
class GetCompositionTreeTestCase(unittest.TestCase):
    def __init__(self, methodName):
        super(GetCompositionTreeTestCase, self).__init__(methodName)

        self.product_repository = mock.NonCallableMagicMock(spec=ProductRepository)
        all_combos = {}
        self.product_repository.get_all_combos = mock.Mock(return_value=all_combos)
        all_options = {}
        self.product_repository.get_all_options = mock.Mock(return_value=all_options)
        all_products = {}
        self.product_repository.get_all_products = mock.Mock(return_value=all_products)
        all_combo_options = {}
        self.product_repository.get_all_combo_options = mock.Mock(return_value=all_combo_options)
        all_combo_products = {}
        self.product_repository.get_all_combo_products = mock.Mock(return_value=all_combo_products)
        all_option_products = {}
        self.product_repository.get_all_option_products = mock.Mock(return_value=all_option_products)
        all_product_ingredients = {}
        self.product_repository.get_all_product_ingredients = mock.Mock(return_value=all_product_ingredients)

    def test_SingleProductComposition_SingleNodeTree(self):
        all_products = {"6012": "6012"}
        self.product_repository.get_all_products = mock.Mock(return_value=all_products)

        composition_tree_builder = CompositionTreeBuilder(self.product_repository)
        composition_tree = composition_tree_builder.get_composition_tree("6012")

        self._validate_node(node=composition_tree, parent=None, number_of_sons=0, part_code="6012", default_qty=None, min_qty=None, max_qty=None, product_type=CompositionType.PRODUCT)

    def test_ComboWithProduct_TreeWithOneSon(self):
        all_combo_products = {}
        combo_product = ProductPart()
        combo_product.parent_part_code = "1051"
        combo_product.part_code = "1050"
        combo_product.min_qty = 1
        combo_product.max_qty = 1
        all_combo_products["1051"] = [combo_product]
        self.product_repository.get_all_combo_products = mock.Mock(return_value=all_combo_products)

        all_combos = {"1051": "1051"}
        self.product_repository.get_all_combos = mock.Mock(return_value=all_combos)

        all_products = {"1050": "1050"}
        self.product_repository.get_all_products = mock.Mock(return_value=all_products)

        composition_tree_builder = CompositionTreeBuilder(self.product_repository)
        composition_tree = composition_tree_builder.get_composition_tree("1051")
        self._validate_node(node=composition_tree, parent=None, number_of_sons=1, part_code="1051", default_qty=None, min_qty=None, max_qty=None, product_type=CompositionType.COMBO)

        son_product = composition_tree.sons[0]
        self._validate_node(node=son_product, parent=composition_tree, number_of_sons=0, part_code="1050", default_qty=0, min_qty=1, max_qty=1, product_type=CompositionType.PRODUCT)

    def test_ComboWithTwoProducts_TreeWithTwoSons(self):
        all_combo_products = {}
        combo_product1 = ProductPart()
        combo_product1.parent_part_code = "1051"
        combo_product1.part_code = "1050"
        combo_product1.min_qty = 1
        combo_product1.max_qty = 1

        combo_product2 = ProductPart()
        combo_product2.parent_part_code = "1051"
        combo_product2.part_code = "1063"
        combo_product2.min_qty = 1
        combo_product2.max_qty = 1
        all_combo_products["1051"] = [combo_product1, combo_product2]
        self.product_repository.get_all_combo_products = mock.Mock(return_value=all_combo_products)

        all_combos = {"1051": "1051"}
        self.product_repository.get_all_combos = mock.Mock(return_value=all_combos)

        all_products = {"1050": "1050", "1063": "1063"}
        self.product_repository.get_all_products = mock.Mock(return_value=all_products)

        composition_tree_builder = CompositionTreeBuilder(self.product_repository)
        composition_tree = composition_tree_builder.get_composition_tree("1051")
        self._validate_node(node=composition_tree, parent=None, number_of_sons=2, part_code="1051", default_qty=None, min_qty=None, max_qty=None, product_type=CompositionType.COMBO)

        self._validate_node(node=composition_tree.sons[0], parent=composition_tree, number_of_sons=0, part_code="1050", default_qty=0, min_qty=1, max_qty=1, product_type=CompositionType.PRODUCT)
        self._validate_node(node=composition_tree.sons[1], parent=composition_tree, number_of_sons=0, part_code="1063", default_qty=0, min_qty=1, max_qty=1, product_type=CompositionType.PRODUCT)

    def test_ProductWithIngredients_TreeWithOneSonWithIngredientGranSons(self):
        all_product_ingredients = {}
        product_ingredient = ProductPart()
        product_ingredient.parent_part_code = "1050"
        product_ingredient.part_code = "8200000"
        product_ingredient.min_qty = 1
        product_ingredient.max_qty = 99
        all_product_ingredients["1050"] = [product_ingredient]
        self.product_repository.get_all_product_ingredients = mock.Mock(return_value=all_product_ingredients)

        all_option_products = {}
        option_product1 = ProductPart()
        option_product1.parent_part_code = "8200000"
        option_product1.part_code = "8700001"
        option_product1.min_qty = 0
        option_product1.max_qty = 9
        option_product2 = ProductPart()
        option_product2.parent_part_code = "8200000"
        option_product2.part_code = "8700002"
        option_product2.min_qty = 0
        option_product2.max_qty = 9
        all_option_products["8200000"] = [option_product1, option_product2]
        self.product_repository.get_all_option_products = mock.Mock(return_value=all_option_products)
        
        all_products = {"1050": "1050", "8700001": "8700001", "8700002": "8700002"}
        self.product_repository.get_all_products = mock.Mock(return_value=all_products)

        all_options = {"8200000": "8200000"}
        self.product_repository.get_all_options = mock.Mock(return_value=all_options)

        default_products ={("1050", "8200000"): {"8700002": "8700002"}}
        self.product_repository.get_default_products = mock.Mock(return_value=default_products)

        composition_tree_builder = CompositionTreeBuilder(self.product_repository)
        composition_tree = composition_tree_builder.get_composition_tree("1050")
        self._validate_node(node=composition_tree, parent=None, number_of_sons=1, part_code="1050", default_qty=None, min_qty=None, max_qty=None, product_type=CompositionType.PRODUCT)

        option = composition_tree.sons[0]
        self._validate_node(node=option, parent=composition_tree, number_of_sons=2, part_code="8200000", default_qty=0, min_qty=1, max_qty=99, product_type=CompositionType.OPTION)

        product1 = option.sons[0]
        self._validate_node(node=product1, parent=option, number_of_sons=0, part_code="8700001", default_qty=0, min_qty=0, max_qty=9, product_type=CompositionType.PRODUCT)

        product2 = option.sons[1]
        self._validate_node(node=product2, parent=option, number_of_sons=0, part_code="8700002", default_qty=1, min_qty=0, max_qty=9, product_type=CompositionType.PRODUCT)

    def test_PartCodeNotInProductOptionOrCombo_ExceptionIsRaised(self):
        all_products = {"6012": "6012"}
        self.product_repository.get_all_products = mock.Mock(return_value=all_products)
        
        all_combos = {"1051": "1051"}
        self.product_repository.get_all_combos = mock.Mock(return_value=all_combos)
        
        all_options = {"820000": "820000"}
        self.product_repository.get_all_options = mock.Mock(return_value=all_options)
        
        try:
            composition_tree_builder = CompositionTreeBuilder(self.product_repository)
            composition_tree_builder.get_composition_tree("6013")
            self.fail()
        except CompositionTreeException as ex:
            self.assertEqual(ex.error_code, CompositionTreeError.InvalidPartCode)

    def test_OptionWithNoProducts_SingleNodeTree(self):
        all_options = {"820000": "820000"}
        self.product_repository.get_all_options = mock.Mock(return_value=all_options)

        all_option_products = {}
        self.product_repository.get_all_option_products = mock.Mock(return_value=all_option_products)

        composition_tree_builder = CompositionTreeBuilder(self.product_repository)
        composition_tree = composition_tree_builder.get_composition_tree("820000")

        self._validate_node(node=composition_tree, parent=None, number_of_sons=0, part_code="820000", default_qty=None, min_qty=None, max_qty=None, product_type=CompositionType.OPTION)

    def test_ComboWithTwoOptionsEachOptionWithTwoProducts_TreeWithTwoSonsAndFourLeafs(self):
        all_combo_options = {}
        combo_option1 = ProductPart()
        combo_option1.parent_part_code = "1051"
        combo_option1.part_code = "730000"
        combo_option1.min_qty = 1
        combo_option1.max_qty = 1

        combo_option2 = ProductPart()
        combo_option2.parent_part_code = "1051"
        combo_option2.part_code = "750000"
        combo_option2.min_qty = 1
        combo_option2.max_qty = 1
        all_combo_options["1051"] = [combo_option1, combo_option2]
        self.product_repository.get_all_combo_options = mock.Mock(return_value=all_combo_options)

        all_option_products = {}
        option_product1 = ProductPart()
        option_product1.parent_part_code = "730000"
        option_product1.part_code = "6012"
        option_product1.min_qty = 0
        option_product1.max_qty = 1
        option_product2 = ProductPart()
        option_product2.parent_part_code = "730000"
        option_product2.part_code = "6013"
        option_product2.min_qty = 0
        option_product2.max_qty = 1
        all_option_products["730000"] = [option_product1, option_product2]

        option_product1 = ProductPart()
        option_product1.parent_part_code = "750000"
        option_product1.part_code = "9008"
        option_product1.min_qty = 0
        option_product1.max_qty = 1
        option_product2 = ProductPart()
        option_product2.parent_part_code = "750000"
        option_product2.part_code = "9013"
        option_product2.min_qty = 0
        option_product2.max_qty = 1
        all_option_products["750000"] = [option_product1, option_product2]

        self.product_repository.get_all_option_products = mock.Mock(return_value=all_option_products)

        all_combos = {"1051": "1051"}
        self.product_repository.get_all_combos = mock.Mock(return_value=all_combos)

        all_options = {"750000": "750000", "730000": "730000"}
        self.product_repository.get_all_options = mock.Mock(return_value=all_options)

        all_products = {"6012": "6012", "6013": "6013", "9008": "9008", "9013": "9013"}
        self.product_repository.get_all_products = mock.Mock(return_value=all_products)

        default_products = {("1051", "750000"): {"9008": "9008"},
                            ("1051", "730000"): {"6012": "6012"}}
        self.product_repository.get_default_products = mock.Mock(return_value=default_products)

        composition_tree_builder = CompositionTreeBuilder(self.product_repository)
        composition_tree = composition_tree_builder.get_composition_tree("1051")

        self._validate_node(node=composition_tree, parent=None, number_of_sons=2, default_qty=None, part_code="1051", min_qty=None, max_qty=None, product_type=CompositionType.COMBO)

        option1 = composition_tree.sons[0]
        self._validate_node(node=option1, parent=composition_tree, number_of_sons=2, part_code="730000", default_qty=0, min_qty=1, max_qty=1, product_type=CompositionType.OPTION)

        leaf1_1 = option1.sons[0]
        self._validate_node(node=leaf1_1, parent=option1, number_of_sons=0, part_code="6012", default_qty=1, min_qty=0, max_qty=1, product_type=CompositionType.PRODUCT)

        leaf1_2 = option1.sons[1]
        self._validate_node(node=leaf1_2, parent=option1, number_of_sons=0, part_code="6013", default_qty=0, min_qty=0, max_qty=1, product_type=CompositionType.PRODUCT)

        option2 = composition_tree.sons[1]
        self._validate_node(node=option2, parent=composition_tree, number_of_sons=2, part_code="750000", default_qty=0, min_qty=1, max_qty=1, product_type=CompositionType.OPTION)

        leaf1_1 = option2.sons[0]
        self._validate_node(node=leaf1_1, parent=option2, number_of_sons=0, part_code="9008", default_qty=1, min_qty=0, max_qty=1, product_type=CompositionType.PRODUCT)

        leaf1_2 = option2.sons[1]
        self._validate_node(node=leaf1_2, parent=option2, number_of_sons=0, part_code="9013", default_qty=0, min_qty=0, max_qty=1, product_type=CompositionType.PRODUCT)

    def _validate_node(self, node, parent, number_of_sons, part_code, default_qty, min_qty, max_qty, product_type):
        self.assertEqual(node.parent, parent)
        self.assertEqual(len(node.sons), number_of_sons)
        self.assertIsNotNone(node.product)
        self.assertEqual(node.product.part_code, part_code)
        self.assertEqual(node.product.default_qty, default_qty)
        self.assertEqual(node.product.min_qty, min_qty)
        self.assertEqual(node.product.max_qty, max_qty)
        self.assertEqual(node.product.type, product_type)
