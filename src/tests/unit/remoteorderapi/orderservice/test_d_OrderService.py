# encoding: utf-8
import os
import unittest
import abc
from msgbus import MBEasyContext
from orderservice2.repository import OrderRepository
from orderservice2 import OrderService, ItemDescriptionCreator


class OrderServiceTestCase(unittest.TestCase):
    __metaclass__ = abc.ABCMeta

    PosDirectory = "D:\\Projects\\Burguer King\\mwpos"

    @classmethod
    def setUpClass(cls):
        os.environ["HVPORT"] = "14000"
        os.environ["HVIP"] = "127.0.0.1"
        os.environ["HVCOMPPORT"] = "35686"
        # Para simularmos um componente, temos que estar com o CWD no bin
        cls.old_cwd = os.getcwd()
        bin_dir = os.path.abspath(OrderServiceTestCase.PosDirectory + "\\bin")
        os.chdir(bin_dir)
        cls.mbcontext = MBEasyContext("test_product_repository")

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.old_cwd)
        cls.mbcontext.MB_EasyFinalize()


class GetStoredOrdersTestCase(OrderServiceTestCase):
    def test_ExecuteGetStoredOrders(self):
        order_repository = OrderRepository(self.mbcontext, 1)
        item_description_creator = ItemDescriptionCreator()

        order_service = OrderService(order_repository, item_description_creator)
        orders = order_service.get_stored_orders()

        self.assertIsNotNone(orders)
