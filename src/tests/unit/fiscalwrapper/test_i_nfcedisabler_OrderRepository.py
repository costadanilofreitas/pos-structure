# encoding: utf-8
import datetime
import os
import sqlite3
import unittest

import mwposdriver
from mwposbuilder import MWPosBuilder
import hvdriver
import abc
from nfcedisabler import OrderRepository
from msgbus import MBEasyContext
from pos_model import OrderKey


class OrderRepositoryTest(unittest.TestCase):
    __metaclass__ = abc.ABCMeta
    DestPosDirectory = "R:\\mwpos"
    DestPosDatabasesDir = os.path.join(DestPosDirectory, "data", "server", "databases")

    @classmethod
    def setUpClass(cls):
        mw_pos_builder = MWPosBuilder(os.path.abspath("..\..\..\..\.."), cls.DestPosDirectory)
        # mw_pos_builder.build_with_components([MWPosBuilder.CompPersistenceNormal])

        cls.mwpos_driver = mwposdriver.MwPosDriver("R:\\mwpos")
        cls.mwpos_driver.start_pos()

        # Variáveis que precisam estar no environment para conseguimos utilizat o mbcontext
        os.environ["HVPORT"] = "14000"
        os.environ["HVIP"] = "127.0.0.1"
        os.environ["HVCOMPPORT"] = "35686"
        # Para simularmos um componente, temos que estar com o CWD no bin
        cls.old_cwd = os.getcwd()
        bin_dir = os.path.join(cls.DestPosDirectory, "bin")
        os.chdir(bin_dir)

        hvdriver.HyperVisorComunicator().wait_persistence()

        cls.mbcontext = MBEasyContext("test_fiscal_repository")
      
        print("finalizado")

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.old_cwd)
        cls.mwpos_driver.terminate_pos()
        cls.mbcontext.MB_EasyFinalize()

    @classmethod
    def get_mbcontext(cls):
        return cls.mbcontext

    def _cleanDatabase(self, cur):
        self._deleteAllCustomProperties(cur)
        self._deleteAllOrders(cur)

    def _deleteAllCustomProperties(self, cur):
        cur.execute("""DELETE FROM OrderCustomProperties""")

    def _deleteAllOrders(self, cur):
        cur.execute("""DELETE FROM Orders""")

    def _createCanceledOrder(self, cur, order_id, date=None):
        # type: (sqlite3.Cursor, int, datetime.datetime) -> None
        if date is None:
            date = datetime.datetime.now()

        cur.execute("""INSERT INTO Orders (OrderId, StateId, OrderType, OriginatorId, SaleType, LineCounter, CreatedAt, LastNewLineAt, 
        LastModifiedLine, BusinessPeriod, DistributionPoint, SessionId, PriceListId1, PriceListTotal, 
        TotalNet, TotalGross, DiscountAmount, TotalTaxIncluded, Fiscal, Backup, Major, Minor) 
        VALUES(?, 4, 0, 'POS0001', 0, 1, ?, ?, 1, '20170405', 'FC', 'pos=1,user=1003,count=1,period=20170405', 'EI', 0.50, 0.48, 0.50, 0.00, 1, 0, 0, ?, 0)""",
                    (order_id, date.strftime("%Y%m%dT%H%M%S.000"), date.strftime("%Y%m%dT%H%M%S.000"), order_id))


class OrderRepository_GetAllOrdersToDisable_Test(OrderRepositoryTest):
    def test_onlyCanceledOrders_allOrdersReturned(self):
        conn = sqlite3.connect(os.path.join(self.DestPosDatabasesDir, "order.db1"))
        cur = conn.cursor()

        self._cleanDatabase(cur)
        self._createCanceledOrder(cur, 1)
        self._createCanceledOrder(cur, 2)
        self._createCanceledOrder(cur, 3)

        cur.close()
        conn.commit()
        conn.close()

        order_repository = OrderRepository(OrderRepository_GetAllOrdersToDisable_Test.mbcontext, ["1"])
        order_list = order_repository.get_all_orders_to_disable()

        self.assertEqual(len(order_list), 3)
        self.assertTrue(OrderKey('1', '1') in order_list, "OrderId '1' from PosId '1'  should be in the returned list but wasn´t")
        self.assertTrue(OrderKey('1', '2') in order_list, "OrderId '2' from PosId '1' should be in the returned list but wasn´t")
        self.assertTrue(OrderKey('1', '3') in order_list, "OrderId '3' from PosId '1' should be in the returned list but wasn´t")

    def test_canceledOrdersOneAlredyDisabled_OnlyNotDisabledReturned(self):
        conn = sqlite3.connect(os.path.join(self.DestPosDatabasesDir, "order.db1"))
        cur = conn.cursor()

        self._cleanDatabase(cur)
        self._createCanceledOrder(cur, 1)
        self._createCanceledOrder(cur, 2)
        self._createCanceledOrder(cur, 3)
        self._disableOrder(cur, 2)

        cur.close()
        conn.commit()
        conn.close()

        order_repository = OrderRepository(OrderRepository_GetAllOrdersToDisable_Test.mbcontext, ["1"])
        order_list = order_repository.get_all_orders_to_disable()

        self.assertEqual(len(order_list), 2)
        self.assertTrue(OrderKey('1', '1') in order_list, "OrderId '1' from PosId '1' should be in the returned list but wasn´t")
        self.assertTrue(OrderKey('1', '3') in order_list, "OrderId '3' from PosId '1' should be in the returned list but wasn´t")

    def test_canceledOrdersAllDisabled_NoOrdersReturned(self):
        conn = sqlite3.connect(os.path.join(self.DestPosDatabasesDir, "order.db1"))
        cur = conn.cursor()

        self._cleanDatabase(cur)
        self._createCanceledOrder(cur, 1)
        self._createCanceledOrder(cur, 2)
        self._createCanceledOrder(cur, 3)
        self._disableOrder(cur, 1)
        self._disableOrder(cur, 2)
        self._disableOrder(cur, 3)

        cur.close()
        conn.commit()
        conn.close()

        order_repository = OrderRepository(OrderRepository_GetAllOrdersToDisable_Test.mbcontext, ["1"])
        order_list = order_repository.get_all_orders_to_disable()

        self.assertEqual(len(order_list), 0)

    def test_oneOrderCanceledTwoPaid_onlyCanceledOrderReturned(self):
        conn = sqlite3.connect(os.path.join(self.DestPosDatabasesDir, "order.db1"))
        cur = conn.cursor()

        self._cleanDatabase(cur)
        self._createPaidOrder(cur, 1)
        self._createPaidOrder(cur, 2)
        self._createCanceledOrder(cur, 3)

        cur.close()
        conn.commit()
        conn.close()

        order_repository = OrderRepository(OrderRepository_GetAllOrdersToDisable_Test.mbcontext, ["1"])
        order_list = order_repository.get_all_orders_to_disable()

        self.assertEqual(len(order_list), 1)
        self.assertTrue(OrderKey('1', '3') in order_list, "OrderId '3' from PosId '1' should be in the returned list but wasn´t")

    def test_oneOrderInEachOfTwoDatabases_twoOrdersReturned(self):
        conn1 = sqlite3.connect(os.path.join(self.DestPosDatabasesDir, "order.db1"))
        cur1 = conn1.cursor()

        conn2 = sqlite3.connect(os.path.join(self.DestPosDatabasesDir, "order.db2"))
        cur2 = conn2.cursor()

        self._cleanDatabase(cur1)
        self._cleanDatabase(cur2)
        self._createCanceledOrder(cur1, 1)
        self._createCanceledOrder(cur2, 2)

        cur1.close()
        cur2.close()
        conn1.commit()
        conn2.commit()
        conn1.close()
        conn2.close()

        order_repository = OrderRepository(OrderRepository_GetAllOrdersToDisable_Test.mbcontext, ["1", "2"])
        order_list = order_repository.get_all_orders_to_disable()

        self.assertEqual(len(order_list), 2)
        self.assertTrue(OrderKey('1', '1') in order_list, "OrderId '1'from PosId '1' should be in the returned list but wasn´t")
        self.assertTrue(OrderKey('2', '2') in order_list, "OrderId '2'from PosId '2' should be in the returned list but wasn´t")

    def test_oneOrderInEachOfTwoDatabasesNoOrderInThird_twoOrdersReturned(self):
        conn1 = sqlite3.connect(os.path.join(self.DestPosDatabasesDir, "order.db1"))
        cur1 = conn1.cursor()

        conn2 = sqlite3.connect(os.path.join(self.DestPosDatabasesDir, "order.db2"))
        cur2 = conn2.cursor()

        self._cleanDatabase(cur1)
        self._cleanDatabase(cur2)
        self._createCanceledOrder(cur1, 1)
        self._createCanceledOrder(cur2, 2)

        cur1.close()
        cur2.close()
        conn1.commit()
        conn2.commit()
        conn1.close()
        conn2.close()

        order_repository = OrderRepository(OrderRepository_GetAllOrdersToDisable_Test.mbcontext, ["1", "2"])
        order_list = order_repository.get_all_orders_to_disable()

        self.assertEqual(len(order_list), 2)
        self.assertTrue(OrderKey('1', '1') in order_list, "OrderId '1' from PosId '1' should be in the returned list but wasn´t")
        self.assertTrue(OrderKey('2', '2') in order_list, "OrderId '2' from PosId '2' should be in the returned list but wasn´t")

    def _createPaidOrder(self, cur, order_id, date=None):
        # type: (sqlite3.Cursor, int, datetime.datetime) -> None
        if date is None:
            date = datetime.datetime.now()

        cur.execute("""INSERT INTO Orders (OrderId, StateId, OrderType, OriginatorId, SaleType, LineCounter, CreatedAt, LastNewLineAt, 
        LastModifiedLine, BusinessPeriod, DistributionPoint, SessionId, PriceListId1, PriceListTotal, 
        TotalNet, TotalGross, DiscountAmount, TotalTaxIncluded, Fiscal, Backup, Major, Minor) 
        VALUES(?, 5, 0, 'POS0001', 0, 1, ?, ?, 1, '20170405', 'FC', 'pos=1,user=1003,count=1,period=20170405', 'EI', 0.50, 0.48, 0.50, 0.00, 1, 0, 0, ?, 0)""",
                    (order_id, date.strftime("%Y%m%dT%H%M%S.000"), date.strftime("%Y%m%dT%H%M%S.000"), order_id))

    def _disableOrder(self, cur, order_id):
        cur.execute("""INSERT INTO OrderCustomProperties (OrderId, Key, Value) VALUES (?, 'ORDER_DISABLED', 'true')""", (str(order_id)))


class OrderRepository_MarkOrderDisabled_Test(OrderRepositoryTest):
    def test_canceledOrder_orderCorrectlyDisabled(self):
        conn = sqlite3.connect(os.path.join(self.DestPosDatabasesDir, "order.db1"))
        cur = conn.cursor()

        self._cleanDatabase(cur)
        self._createCanceledOrder(cur, 1)

        cur.close()
        conn.commit()
        conn.close()

        order_repository = OrderRepository(OrderRepository_GetAllOrdersToDisable_Test.mbcontext, ["1"])
        order_list = order_repository.mark_order_disabled("1", "1")

        conn = sqlite3.connect(os.path.join(self.DestPosDatabasesDir, "order.db1"))
        cur = conn.cursor()

        self.assertTrue(self._is_order_disabled(cur, "1"), "OrderId '1' should be disabled in the database")

    def _is_order_disabled(self, cur, order_id):
        # type: (sqlite3.Cursor, str) -> bool
        cur.execute("""SELECT count(1)
from Orders o 
inner join OrderCustomProperties ocp 
on o.OrderId = ocp.OrderId
where o.OrderId = ? and ocp.Key = "ORDER_DISABLED" and ocp.Value = "true" """, order_id)
        return int(cur.fetchone()[0]) > 0


class OrderRepository_MarkOrderNotDisabled_Test(OrderRepositoryTest):
    def test_canceledOrder_orderCorrectlyDisabled(self):
        conn = sqlite3.connect(os.path.join(self.DestPosDatabasesDir, "order.db1"))
        cur = conn.cursor()

        self._cleanDatabase(cur)
        self._createCanceledOrder(cur, 1)

        cur.close()
        conn.commit()
        conn.close()

        order_repository = OrderRepository(OrderRepository_GetAllOrdersToDisable_Test.mbcontext, ["1"])
        order_list = order_repository.mark_order_not_disabled("1", "1")

        conn = sqlite3.connect(os.path.join(self.DestPosDatabasesDir, "order.db1"))
        cur = conn.cursor()

        self.assertTrue(self._is_order_not_disabled(cur, "1"), "OrderId '1' should be disabled in the database")

    def _is_order_not_disabled(self, cur, order_id):
        # type: (sqlite3.Cursor, str) -> bool
        cur.execute("""SELECT count(1)
        from Orders o 
        inner join OrderCustomProperties ocp 
        on o.OrderId = ocp.OrderId
        where o.OrderId = ? and ocp.Key = "ORDER_DISABLED" and ocp.Value = "false" """, order_id)
        return int(cur.fetchone()[0]) > 0

