# encoding: utf-8
import unittest
import abc
import os
import sqlite3
from msgbus import MBEasyContext
from remoteorder.compositiontree import DbProductRepository, ProductPart
from mwposdriver import MwPosDriver
import hvdriver


# TODO: Reexecutar este teste depois da alteração no min_qty para 0 quando não existe QtyOptions
# TODO: Criar teste para funcionalidade de excluir ingredientes DTOnly
class ProductRepositoryTestCase(unittest.TestCase):
    __metaclass__ = abc.ABCMeta

    RamDiskPosDirectory = "R:\\hv+persist"

    @classmethod
    def setUpClass(cls):
        cls.mwpos_driver = MwPosDriver(ProductRepositoryTestCase.RamDiskPosDirectory)
        cls.mwpos_driver.start_pos()

        # Variáveis que precisam estar no environment para conseguimos utilizat o mbcontext
        os.environ["HVPORT"] = "14000"
        os.environ["HVIP"] = "127.0.0.1"
        os.environ["HVCOMPPORT"] = "35686"
        # Para simularmos um componente, temos que estar com o CWD no bin
        cls.old_cwd = os.getcwd()
        bin_dir = os.path.abspath(ProductRepositoryTestCase.RamDiskPosDirectory + "\\bin")
        os.chdir(bin_dir)

        hvdriver.HyperVisorComunicator().wait_persistence()

        cls.mbcontext = MBEasyContext("test_product_repository")

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.old_cwd)
        cls.mwpos_driver.terminate_pos()
        cls.mbcontext.MB_EasyFinalize()

    @classmethod
    def get_mbcontext(cls):
        return cls.mbcontext

    def _cleanDatabase(self, cur):
        # type: (sqlite3.Cursor) -> None
        query = """delete from Production;
delete from Price;
delete from PriceList;
delete from ProductPart;
delete from ProductTags;
delete from ProductClassification;
delete from ProductKernelParams;
delete from Product;"""

        all_statements = query.split(";")
        for statement in all_statements:
            cur.execute(statement)

    def _execute_in_transaction(self, method):
        conn = sqlite3.connect(ProductRepositoryTestCase.RamDiskPosDirectory + "\\data\\server\\databases\\product.db")
        cur = conn.cursor()

        method(cur)

        cur.close()
        conn.commit()
        conn.close()

    def _execute_with_clean_database(self, method):
        def clean_database_and_execute(cur):
            self._cleanDatabase(cur)
            method(cur)

        self._execute_in_transaction(clean_database_and_execute)

    def _create_product(self, cur, part_code, product_name):
        cur.execute("""insert into Product (ProductCode, ProductName) values (?, ?)""", (part_code, product_name))
        self._create_product_kernel_params(cur, part_code, 0)

    def _create_option(self, cur, part_code, product_name):
        cur.execute("""insert into Product (ProductCode, ProductName) values (?, ?)""", (part_code, product_name))
        self._create_product_kernel_params(cur, part_code, 1)

    def _create_combo(self, cur, part_code, product_name):
        cur.execute("""insert into Product (ProductCode, ProductName) values (?, ?)""", (part_code, product_name))
        self._create_product_kernel_params(cur, part_code, 2)

    def _create_tag(self, cur, part_code, tag_value):
        cur.execute("""insert or replace into ProductTags (ProductCode, Tag) VALUES 
        (?, ?)""", (part_code, tag_value))

    def _create_product_classification(self, cur, class_code, part_code):
        cur.execute("""insert or replace into ProductClassification (ClassCode, ProductCode) VALUES 
                (?, ?)""", (class_code, part_code))

    def _create_product_kernel_params(self, cur, part_code, product_type):
        cur.execute("""insert or replace into ProductKernelParams (ProductCode, ProductType, Enabled, ProductPriority, PromoSortMode, MeasureUnit, SysProdExplosionActive) VALUES 
(?, ?, ?, ?, ?, ?, ?)""", (part_code, product_type, 1, 100, 1, "UN", 1))

    def _assertCorrectProductPart(self, product_part, parent_part_code, part_code, min_qty, max_qty):
        # type: (ProductPart, unicode, unicode, int, int) -> None
        self.assertIsNotNone(product_part)
        self.assertEqual(product_part.parent_part_code, parent_part_code)
        self.assertEqual(product_part.part_code, part_code)
        self.assertEqual(product_part.min_qty, min_qty)
        self.assertEqual(product_part.max_qty, max_qty)


class GetAllProductsTestCase(ProductRepositoryTestCase):
    def test_TwoProductInDatabase_TwoProductAreReturned(self):
        def insert_products(cur):
            self._create_product(cur, 1050, "Whopper/Q")
            self._create_product(cur, 1052, "Whopper/DQ")
        self._execute_with_clean_database(insert_products)

        product_repository = DbProductRepository(self.mbcontext)
        all_products = product_repository.get_all_products()

        self.assertIsNotNone(all_products)
        self.assertEqual(len(all_products), 2)
        self.assertTrue("1050" in all_products)
        self.assertTrue("1052" in all_products)

    def test_ProductOptionAndCombo_OnlyProductIsReturned(self):
        def insert_products(cur):
            self._create_product(cur, 1050, "Whopper/Q")
            self._create_combo(cur, 1051, "CM Whopper/Q")
            self._create_option(cur, 820000, "Ingredientes")

        self._execute_with_clean_database(insert_products)

        product_repository = DbProductRepository(self.mbcontext)
        all_products = product_repository.get_all_products()

        self.assertIsNotNone(all_products)
        self.assertEqual(len(all_products), 1)
        self.assertTrue("1050" in all_products)


class GetAllOptionsTestCase(ProductRepositoryTestCase):
    def test_TwoOptionsInDatabase_TwoProductAreReturned(self):
        def insert_products(cur):
            self._create_option(cur, 8200000, "Ingredientes")
            self._create_option(cur, 7300000, "Fritos")
        self._execute_with_clean_database(insert_products)

        product_repository = DbProductRepository(self.mbcontext)
        all_options = product_repository.get_all_options()

        self.assertIsNotNone(all_options)
        self.assertEqual(len(all_options), 2)
        self.assertTrue("8200000" in all_options)
        self.assertTrue("7300000" in all_options)

    def test_ProductOptionAndCombo_OnlyProductIsReturned(self):
        def insert_products(cur):
            self._create_product(cur, 1050, "Whopper/Q")
            self._create_combo(cur, 1051, "CM Whopper/Q")
            self._create_option(cur, 820000, "Ingredientes")

        self._execute_with_clean_database(insert_products)

        product_repository = DbProductRepository(self.mbcontext)
        all_options = product_repository.get_all_options()

        self.assertIsNotNone(all_options)
        self.assertEqual(len(all_options), 1)
        self.assertTrue("820000" in all_options)


class GetAllCombosTestCase(ProductRepositoryTestCase):
    def test_TwoOptionsInDatabase_TwoProductAreReturned(self):
        def insert_products(cur):
            self._create_combo(cur, 1051, "CM Whopper/Q")
            self._create_combo(cur, 1053, "CM Whopper/DP")
        self._execute_with_clean_database(insert_products)

        product_repository = DbProductRepository(self.mbcontext)
        all_combos = product_repository.get_all_combos()

        self.assertIsNotNone(all_combos)
        self.assertEqual(len(all_combos), 2)
        self.assertTrue("1051" in all_combos)
        self.assertTrue("1053" in all_combos)

    def test_ProductOptionAndCombo_OnlyProductIsReturned(self):
        def insert_products(cur):
            self._create_product(cur, 1050, "Whopper/Q")
            self._create_combo(cur, 1051, "CM Whopper/Q")
            self._create_option(cur, 820000, "Ingredientes")

        self._execute_with_clean_database(insert_products)

        product_repository = DbProductRepository(self.mbcontext)
        all_combos = product_repository.get_all_combos()

        self.assertIsNotNone(all_combos)
        self.assertEqual(len(all_combos), 1)
        self.assertTrue("1051" in all_combos)


class GetAllProductIngredients(ProductRepositoryTestCase):
    def test_ProductWithNoIngredients_NoItemInDictionart(self):
        def insert_products(cur):
            self._create_product(cur, 1050, "CM Whopper/Q")

        self._execute_with_clean_database(insert_products)

        product_repository = DbProductRepository(self.mbcontext)
        all_product_ingredients = product_repository.get_all_product_ingredients()

        self.assertIsNotNone(all_product_ingredients)
        self.assertEqual(len(all_product_ingredients), 0)

    def test_ProductWithIngredients_ProductAndIngredientReturned(self):
        def insert_products(cur):
            self._create_product(cur, 1050, "CM Whopper/Q")
            self._create_option(cur, 820000, "Ingedientes")
            self._create_tag(cur, 1050, "QtyOptions=820000>0;1;99")

        self._execute_with_clean_database(insert_products)

        product_repository = DbProductRepository(self.mbcontext)
        all_product_ingredients = product_repository.get_all_product_ingredients()

        self.assertIsNotNone(all_product_ingredients)
        self.assertEqual(len(all_product_ingredients), 1)
        self.assertTrue("1050" in all_product_ingredients)
        self.assertEqual(len(all_product_ingredients["1050"]), 1)
        ingredient = all_product_ingredients["1050"][0]
        self._assertCorrectProductPart(product_part=ingredient, parent_part_code="1050", part_code="820000", min_qty=1, max_qty=99)

    def test_ProductWithTwoIngredients_ProductAndIngredientReturned(self):
        def insert_products(cur):
            self._create_product(cur, 1050, "CM Whopper/Q")
            self._create_option(cur, 820000, "Ingedientes")
            self._create_tag(cur, 1050, "QtyOptions=820000>1;1;1|830000>2;3;4")

        self._execute_with_clean_database(insert_products)

        product_repository = DbProductRepository(self.mbcontext)
        all_product_ingredients = product_repository.get_all_product_ingredients()

        self.assertIsNotNone(all_product_ingredients)
        self.assertEqual(len(all_product_ingredients), 1)
        self.assertTrue("1050" in all_product_ingredients)
        self.assertEqual(len(all_product_ingredients["1050"]), 2)
        ingredient1 = filter(lambda x: x.part_code == "820000", all_product_ingredients["1050"])
        self.assertEqual(len(ingredient1), 1)
        self._assertCorrectProductPart(product_part=ingredient1[0], parent_part_code="1050", part_code="820000", min_qty=1, max_qty=1)
        ingredient2 = filter(lambda x: x.part_code == "830000", all_product_ingredients["1050"])
        self.assertEqual(len(ingredient1), 1)
        self._assertCorrectProductPart(product_part=ingredient2[0], parent_part_code="1050", part_code="830000", min_qty=3, max_qty=4)

    def test_TwoProductWithSameIngredient_ProductsAndIngredientsReturned(self):
        def insert_products(cur):
            self._create_product(cur, 1050, "CM Whopper/Q")
            self._create_product(cur, 1053, "CM Whopper/DQ")
            self._create_option(cur, 820000, "Ingedientes")
            self._create_tag(cur, 1050, "QtyOptions=820000>1;2;3")
            self._create_tag(cur, 1053, "QtyOptions=820000>2;3;4")

        self._execute_with_clean_database(insert_products)

        product_repository = DbProductRepository(self.mbcontext)
        all_product_ingredients = product_repository.get_all_product_ingredients()

        self.assertIsNotNone(all_product_ingredients)
        self.assertEqual(len(all_product_ingredients), 2)
        self.assertTrue("1050" in all_product_ingredients)
        self.assertEqual(len(all_product_ingredients["1050"]), 1)
        ingredient = filter(lambda x: x.part_code == "820000", all_product_ingredients["1050"])
        self.assertEqual(len(ingredient), 1)
        self._assertCorrectProductPart(product_part=ingredient[0], parent_part_code="1050", part_code="820000", min_qty=2, max_qty=3)

        self.assertTrue("1053" in all_product_ingredients)
        self.assertEqual(len(all_product_ingredients["1053"]), 1)
        ingredient = filter(lambda x: x.part_code == "820000", all_product_ingredients["1053"])
        self.assertEqual(len(ingredient), 1)
        self._assertCorrectProductPart(product_part=ingredient[0], parent_part_code="1053", part_code="820000", min_qty=3, max_qty=4)


class GetAllOptionProductsTestCase(ProductRepositoryTestCase):
    def test_OptionWithNoProducts_OptionNotInDictionary(self):
        def insert_products(cur):
            self._create_option(cur, 820000, "Ingredientes")

        self._execute_with_clean_database(insert_products)

        product_repository = DbProductRepository(self.mbcontext)
        all_option_products = product_repository.get_all_option_products()

        self.assertIsNotNone(all_option_products)
        self.assertEqual(len(all_option_products), 0)

    def test_OptionWithTwoProductsNoItemQty_OptionAndProductsInDictionaryDefaultQuantities(self):
        def insert_products(cur):
            self._create_option(cur, 820000, "Ingredientes")
            self._create_product(cur, 870001, "Hamburger")
            self._create_product(cur, 870002, "Mostarda")
            self._create_product_classification(cur, 820000, 870001)
            self._create_product_classification(cur, 820000, 870002)

        self._execute_with_clean_database(insert_products)

        product_repository = DbProductRepository(self.mbcontext)
        all_option_products = product_repository.get_all_option_products()

        self.assertIsNotNone(all_option_products)
        self.assertEqual(len(all_option_products), 1)
        self.assertTrue("820000" in all_option_products)
        self.assertEqual(len(all_option_products["820000"]), 2)

        ingredient1 = filter(lambda x: x.part_code == "870001", all_option_products["820000"])
        self.assertEqual(len(ingredient1), 1)
        self._assertCorrectProductPart(product_part=ingredient1[0], parent_part_code="820000", part_code="870001", min_qty=0, max_qty=1)

        ingredient2 = filter(lambda x: x.part_code == "870002", all_option_products["820000"])
        self.assertEqual(len(ingredient2), 1)
        self._assertCorrectProductPart(product_part=ingredient2[0], parent_part_code="820000", part_code="870002", min_qty=0, max_qty=1)

    def test_OptionWithTwoProductsWithItemQty_OptionAndProductsInDictionaryCorrectQuantities(self):
        def insert_products(cur):
            self._create_option(cur, 820000, "Ingredientes")
            self._create_product(cur, 870001, "Hamburger")
            self._create_product(cur, 870002, "Mostarda")
            self._create_product_classification(cur, 820000, 870001)
            self._create_product_classification(cur, 820000, 870002)
            self._create_tag(cur, 820000, "ItemQtys=0;9")

        self._execute_with_clean_database(insert_products)

        product_repository = DbProductRepository(self.mbcontext)
        all_option_products = product_repository.get_all_option_products()

        self.assertIsNotNone(all_option_products)
        self.assertEqual(len(all_option_products), 1)
        self.assertTrue("820000" in all_option_products)
        self.assertEqual(len(all_option_products["820000"]), 2)

        ingredient1 = filter(lambda x: x.part_code == "870001", all_option_products["820000"])
        self.assertEqual(len(ingredient1), 1)
        self._assertCorrectProductPart(product_part=ingredient1[0], parent_part_code="820000", part_code="870001", min_qty=0, max_qty=9)

        ingredient2 = filter(lambda x: x.part_code == "870002", all_option_products["820000"])
        self.assertEqual(len(ingredient2), 1)
        self._assertCorrectProductPart(product_part=ingredient2[0], parent_part_code="820000", part_code="870002", min_qty=0, max_qty=9)

    def test_TwoOptionWithTwoProductsWithItemQtys_OptionAndProductsInDictionaryWithCorrectQuantities(self):
        def insert_products(cur):
            self._create_option(cur, 820000, "Ingredientes")
            self._create_option(cur, 830000, "Ingredientes2")
            self._create_product(cur, 870001, "Hamburger")
            self._create_product(cur, 870002, "Mostarda")
            self._create_tag(cur, 820000, "ItemQtys=0;9")
            self._create_tag(cur, 830000, "ItemQtys=1;2")
            self._create_product_classification(cur, 820000, 870001)
            self._create_product_classification(cur, 820000, 870002)
            self._create_product_classification(cur, 830000, 870001)
            self._create_product_classification(cur, 830000, 870002)

        self._execute_with_clean_database(insert_products)

        product_repository = DbProductRepository(self.mbcontext)
        all_option_products = product_repository.get_all_option_products()

        self.assertIsNotNone(all_option_products)
        self.assertEqual(len(all_option_products), 2)
        self.assertTrue("820000" in all_option_products)
        self.assertEqual(len(all_option_products["820000"]), 2)

        ingredient1_1 = filter(lambda x: x.part_code == "870001", all_option_products["820000"])
        self.assertEqual(len(ingredient1_1), 1)
        self._assertCorrectProductPart(product_part=ingredient1_1[0], parent_part_code="820000", part_code="870001", min_qty=0, max_qty=9)

        ingredient1_2 = filter(lambda x: x.part_code == "870002", all_option_products["820000"])
        self.assertEqual(len(ingredient1_2), 1)
        self._assertCorrectProductPart(product_part=ingredient1_2[0], parent_part_code="820000", part_code="870002", min_qty=0, max_qty=9)

        self.assertTrue("830000" in all_option_products)
        self.assertEqual(len(all_option_products["830000"]), 2)

        ingredient2_1 = filter(lambda x: x.part_code == "870001", all_option_products["830000"])
        self.assertEqual(len(ingredient2_1), 1)
        self._assertCorrectProductPart(product_part=ingredient2_1[0], parent_part_code="830000", part_code="870001", min_qty=1, max_qty=2)

        ingredient2_2 = filter(lambda x: x.part_code == "870002", all_option_products["830000"])
        self.assertEqual(len(ingredient2_2), 1)
        self._assertCorrectProductPart(product_part=ingredient2_2[0], parent_part_code="830000", part_code="870002", min_qty=1, max_qty=2)


class GetAllComboOptionsTestCase(ProductRepositoryTestCase):
    def test_ComboWithNoOptions_NoItemInDictionary(self):
        def insert_products(cur):
            self._create_combo(cur, 1053, "CM Whopper/DQ")

        self._execute_with_clean_database(insert_products)

        product_repository = DbProductRepository(self.mbcontext)
        all_combo_options = product_repository.get_all_combo_options()

        self.assertIsNotNone(all_combo_options)
        self.assertEqual(len(all_combo_options), 0)

    def test_ComboWithOptions_ComboAndIngredientsReturned(self):
        def insert_products(cur):
            self._create_combo(cur, 1053, "CM Whopper/Q")
            self._create_option(cur, 750000, "Bebidas")
            self._create_tag(cur, 1053, "QtyOptions=750000>0;1;99")

        self._execute_with_clean_database(insert_products)

        product_repository = DbProductRepository(self.mbcontext)
        all_combo_options = product_repository.get_all_combo_options()

        self.assertIsNotNone(all_combo_options)
        self.assertEqual(len(all_combo_options), 1)
        self.assertTrue("1053" in all_combo_options)
        self.assertEqual(len(all_combo_options["1053"]), 1)
        option = all_combo_options["1053"][0]
        self._assertCorrectProductPart(product_part=option, parent_part_code="1053", part_code="750000", min_qty=1, max_qty=99)

    def test_ProductWithTwoIngredients_ProductAndIngredientReturned(self):
        def insert_products(cur):
            self._create_combo(cur, 1053, "CM Whopper/Q")
            self._create_option(cur, 750000, "Bebidas")
            self._create_option(cur, 730000, "Fritos")
            self._create_tag(cur, 1053, "QtyOptions=750000>1;1;1|730000>2;3;4")

        self._execute_with_clean_database(insert_products)

        product_repository = DbProductRepository(self.mbcontext)
        all_combo_options = product_repository.get_all_combo_options()

        self.assertIsNotNone(all_combo_options)
        self.assertEqual(len(all_combo_options), 1)
        self.assertTrue("1053" in all_combo_options)
        self.assertEqual(len(all_combo_options["1053"]), 2)
        option1 = filter(lambda x: x.part_code == "750000", all_combo_options["1053"])
        self.assertEqual(len(option1), 1)
        self._assertCorrectProductPart(product_part=option1[0], parent_part_code="1053", part_code="750000", min_qty=1, max_qty=1)
        option2 = filter(lambda x: x.part_code == "730000", all_combo_options["1053"])
        self.assertEqual(len(option2), 1)
        self._assertCorrectProductPart(product_part=option2[0], parent_part_code="1053", part_code="730000", min_qty=3, max_qty=4)

    def test_TwoProductWithSameIngredient_ProductsAndIngredientsReturned(self):
        def insert_products(cur):
            self._create_combo(cur, 1050, "CM Whopper/Q")
            self._create_combo(cur, 1053, "CM Whopper/DQ")
            self._create_option(cur, 750000, "Bebidas")
            self._create_tag(cur, 1050, "QtyOptions=750000>1;2;3")
            self._create_tag(cur, 1053, "QtyOptions=750000>2;3;4")

        self._execute_with_clean_database(insert_products)

        product_repository = DbProductRepository(self.mbcontext)
        all_combo_options = product_repository.get_all_combo_options()

        self.assertIsNotNone(all_combo_options)
        self.assertEqual(len(all_combo_options), 2)
        self.assertTrue("1050" in all_combo_options)
        self.assertEqual(len(all_combo_options["1050"]), 1)
        ingredient = filter(lambda x: x.part_code == "750000", all_combo_options["1050"])
        self.assertEqual(len(ingredient), 1)
        self._assertCorrectProductPart(product_part=ingredient[0], parent_part_code="1050", part_code="750000", min_qty=2, max_qty=3)

        self.assertTrue("1053" in all_combo_options)
        self.assertEqual(len(all_combo_options["1053"]), 1)
        ingredient = filter(lambda x: x.part_code == "750000", all_combo_options["1053"])
        self.assertEqual(len(ingredient), 1)
        self._assertCorrectProductPart(product_part=ingredient[0], parent_part_code="1053", part_code="750000", min_qty=3, max_qty=4)


class GetAllComboProductsTestCase(ProductRepositoryTestCase):
    # TODO: Criar testes para este metodos
    pass