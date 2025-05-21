# encoding: utf-8
import os
import unittest
import sqlite3
import mwposdriver
import hvdriver
import sqlite3
from DbTestCase import DbTestCase
from posot import OrderTaker
from sysactions import get_model, get_posot, get_pricelist
from msgbus import MBEasyContext, FM_PARAM, TK_POS_BUSINESSBEGIN, TK_SYS_ACK, TK_POS_USERLOGIN, TK_POS_USEROPEN
from bustoken import TK_FISCALWRAPPER_PROCESS_REQUEST
from datetime import datetime
from remoteorder.model import CurrentOrderItem
import sysactions


class OrderTakerTestCase(DbTestCase):
    RamDiskPosDirectory = "R:\\mwpos"
    OrderDb1Path = "R:\\mwpos\\data\\server\\databases\\order.db1"
    OrderDb2Path = "R:\\mwpos\\data\\server\\databases\\order.db2"
    PersistCompDbPath = "R:\\mwpos\\data\\server\\databases\\persistcomp.db"
    PosCtrlDbPath = "R:\\mwpos\\data\\server\\databases\\posctrl.db"
    FiscalDbPath = "R:\\mwpos\\data\\server\\databases\\fiscal_persistcomp.db"

    @classmethod
    def setUpClass(cls):
        cls.mwpos_driver = mwposdriver.MwPosDriver(OrderTakerTestCase.RamDiskPosDirectory)
        cls.mwpos_driver.delete_all_databases()
        cls.mwpos_driver.start_pos()

        # Variáveis que precisam estar no environment para conseguimos utilizat o mbcontext
        os.environ["HVPORT"] = "14000"
        os.environ["HVIP"] = "127.0.0.1"
        os.environ["HVCOMPPORT"] = "35686"
        # Para simularmos um componente, temos que estar com o CWD no bin
        cls.old_cwd = os.getcwd()
        bin_dir = os.path.abspath(OrderTakerTestCase.RamDiskPosDirectory + "\\bin")
        os.chdir(bin_dir)

        hvdriver.HyperVisorComunicator().wait_persistence()

        cls.mbcontext = MBEasyContext("OrderTakerTestCase")
        sysactions.mbcontext = cls.mbcontext

        try:
            cls._open_day_login()
        except:
            cls.tearDownClass()

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.old_cwd)
        cls.mwpos_driver.terminate_pos()
        cls.mbcontext.MB_EasyFinalize()

    @staticmethod
    def clean_database(cur, params):
        # type: (sqlite3.Cursor) -> None
        query = """
DELETE FROM CurrentOrderItem;
DELETE FROM OrderTender;
DELETE FROM OrderItem;
DELETE FROM OrderVoidHistory;
DELETE FROM OrderStateHistory;
DELETE FROM Orders;
"""
        all_statements = query.split(";")
        for statement in all_statements:
            cur.execute(statement)


    @staticmethod
    def clean_persistcomp_database(cur, params):
        # type: (sqlite3.Cursor) -> None
        cur.execute("Update Sequencer set SeqNo = 0")

    @staticmethod
    def clean_posctrl_db(cur, params):
        cur.execute("Update PosState set State = 0, BusinessPeriod = 0, OperatorId = NULL, OpState = 0, MainScreenId = NULL, OperatorName = NULL")

    def test_CreateOrderCalled_OrderCreatedInDatabse(self):
        self.execute_in_transaction(self.clean_database, OrderTakerTestCase.OrderDb1Path)
        self.execute_in_transaction(self.clean_persistcomp_database, OrderTakerTestCase.PersistCompDbPath)
        
        order_taker = get_posot(get_model(1))  # type: OrderTaker
        order_taker.blkopnotify = True
        order_taker.createOrder(posid=1, pricelist="1", orderType="SALE", saletype="DELIVERY", orderSubType="Teste")

        def check_order_created(cur, params):
            # type: (sqlite3.Cursor) -> None
            cur.execute("select count(1) from Orders")
            row = cur.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row[0], 1)

            cur.execute("select OrderId, OrderType, OrderSubType, SaleType from Orders")
            row = cur.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row[0], 1)
            self.assertEqual(row[1], 0)
            self.assertEqual(row[2], "Teste")
            # TODO: Verificar por que o SaleType não é atualizado
            #self.assertEqual(row[3], 4)

        self.execute_in_transaction(check_order_created, OrderTakerTestCase.OrderDb1Path)

    def test_CompleteSale_SaleCreatedInDatabase(self):
        self.execute_in_transaction(self.clean_database, OrderTakerTestCase.OrderDb1Path)
        self.execute_in_transaction(self.clean_persistcomp_database, OrderTakerTestCase.PersistCompDbPath)

        model = get_model(1)
        order_taker = get_posot(model)  # type: OrderTaker
        order_taker.blkopnotify = True
        attributes = order_taker.createOrder(posid=1, pricelist="1", orderType="SALE", saletype="DELIVERY", orderSubType="Teste")
        self.assertIsNotNone(attributes)
        self.assertTrue("orderId" in attributes)
        self.assertEqual(attributes["orderId"], "1")

        # do_sale_xml = order_taker.doSale(posid=1, itemid="1.6012", pricelist=get_pricelist(model), qtty=1, verifyOption=False, dimension="", saletype="EAT_IN")
        def insert_current_order_item(cur, param):
            current_order_item = CurrentOrderItem()
            current_order_item.order_id = 1
            current_order_item.line_number = 1
            current_order_item.item_id = "1"
            current_order_item.level = 0
            current_order_item.part_code = "6012"
            current_order_item.ordered_quantity = 1
            current_order_item.last_ordered_quantity = None
            current_order_item.included_quantity = 1
            current_order_item.decremented_quantity = 0
            current_order_item.price_key = "186038"
            current_order_item.discount_ammount = 0.00
            current_order_item.surcharge_ammount = 0.00
            current_order_item.only_flag = 0
            current_order_item.overwrittern_unit_price = None
            current_order_item.default_qty = 1

            cur.execute("""insert into CurrentOrderItem
(OrderId, LineNumber, ItemId, Level, PartCode, OrderedQty, LastOrderedQty, IncQty, DecQty, PriceKey, DiscountAmount, SurchargeAmount, OnlyFlag, OverwrittenUnitPrice, DefaultQty)
VALUES
(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                        (current_order_item.order_id,
                         current_order_item.line_number,
                         current_order_item.item_id,
                         current_order_item.level,
                         current_order_item.part_code,
                         current_order_item.ordered_quantity,
                         current_order_item.last_ordered_quantity,
                         current_order_item.included_quantity,
                         current_order_item.decremented_quantity,
                         current_order_item.price_key,
                         current_order_item.discount_ammount,
                         current_order_item.surcharge_ammount,
                         current_order_item.only_flag,
                         current_order_item.overwrittern_unit_price,
                         current_order_item.default_qty))

        self.execute_in_transaction(insert_current_order_item, OrderTakerTestCase.OrderDb1Path)

        do_total_xml = order_taker.doTotal(1)
        do_tender_response = order_taker.doTender(posid=1, tenderid=0, amount=float(do_total_xml), donotclose=True)
        if float(do_tender_response["dueAmount"]) != 0.0:
            raise Exception("Erro processando pagamento")

        def save_payment_data(cur, params):
            cur.execute("insert into PaymentData (PosId, OrderId, TenderSeqId, Type, Amount, Change) VALUES (?, ?, ?, ?, ?, ?)",
                        (1, attributes["orderId"], do_tender_response["tenderId"], 0, float(do_total_xml), 0.0))

        self.execute_in_transaction(save_payment_data, OrderTakerTestCase.FiscalDbPath)

        ret = self.mbcontext.MB_EasySendMessage("FiscalWrapper", TK_FISCALWRAPPER_PROCESS_REQUEST, format=FM_PARAM, data="1")

        fiscal_ok = ret.data.split("\0")[0]
        if fiscal_ok:
            update_tender_response = order_taker.doTender(posid=1, tenderid=0, amount=float(do_total_xml), donotclose=True, ordertenderid=do_tender_response["tenderId"])
            if float(update_tender_response["dueAmount"]) != 0.0:
                raise Exception("Erro processando pagamento")


    @classmethod
    def _open_day_login(cls):
        pos_id = 1
        user_id = "5813"
        long_username = "Desenvolvedor"

        today = datetime.today().strftime("%Y%m%d")
        msg = cls.mbcontext.MB_EasySendMessage("POS%d" % pos_id, TK_POS_BUSINESSBEGIN, FM_PARAM, "%s\0%s" % (pos_id, today), timeout=90000000)
        if msg.token != TK_SYS_ACK:
            raise Exception("Error opening day")

        msg = cls.mbcontext.MB_EasySendMessage("POS%d" % pos_id, TK_POS_USEROPEN, FM_PARAM, "%s\0%s\0%s\0%s" % (pos_id, user_id, 0.0, long_username))
        if msg.token != TK_SYS_ACK:
            raise Exception("Error opening user")
        
        msg = cls.mbcontext.MB_EasySendMessage("POS%d" % pos_id, TK_POS_USERLOGIN, FM_PARAM, "%s\0%s\0%s" % (pos_id, user_id, long_username))
        if msg.token != TK_SYS_ACK:
            raise Exception("Error logging in")
