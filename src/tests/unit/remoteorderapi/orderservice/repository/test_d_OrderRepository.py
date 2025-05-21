# encoding: utf-8
import os
import unittest
import abc
from msgbus import MBEasyContext
from orderservice2.repository import OrderRepository


class OrderRepositoryTestCase(unittest.TestCase):
    __metaclass__ = abc.ABCMeta

    PosDirectory = "D:\\Projects\\Burguer King\\mwpos"

    @classmethod
    def setUpClass(cls):
        os.environ["HVPORT"] = "14000"
        os.environ["HVIP"] = "127.0.0.1"
        os.environ["HVCOMPPORT"] = "35686"
        # Para simularmos um componente, temos que estar com o CWD no bin
        cls.old_cwd = os.getcwd()
        bin_dir = os.path.abspath(OrderRepositoryTestCase.PosDirectory + "\\bin")
        os.chdir(bin_dir)
        cls.mbcontext = MBEasyContext("test_product_repository")

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.old_cwd)
        cls.mbcontext.MB_EasyFinalize()


class GetStoredOrdersTestCase(OrderRepositoryTestCase):
    def test_ExecuteGetStoredOrders(self):
        order_repository = OrderRepository(self.mbcontext, 1)
        orders = order_repository.get_stored_orders()

        self.assertIsNotNone(orders)
