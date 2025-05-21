import unittest
import mock

from nfcedisabler import NfceDisabler, OrderDisabler, OrderRepository
from old_helper import OrderTaker
from pos_model import OrderKey
from xml.etree import cElementTree as eTree
from requests.exceptions import RequestException


class OrderDisablerTest(unittest.TestCase):
    def test_singleOrderIdReturned_orderPictureAsked(self):
        order_repository = self._aOrderRepositoryReturning([OrderKey("1", "13")])
        nfce_disabler = self._aNfceDisabler().build()
        order_taker = self._aOrderTaker().build()

        order_disabler = OrderDisabler(order_repository, nfce_disabler, order_taker)
        order_disabler.disable_all_orders()

        order_taker.get_order_picture.assert_called_with("1", "13")

    def test_singleOrderIdReturned_disableFiscalNumberAskedWithCorrectOrderXml(self):
        order_repository = self._aOrderRepositoryReturning([OrderKey("1", "13")])
        nfce_disabler = self._aNfceDisabler().build()
        order_xml = "<order></order>"
        order_taker = self._aOrderTaker().with_return_value(order_xml).build()

        order_taker.get_order_picture = mock.Mock(return_value=order_xml)

        order_disabler = OrderDisabler(order_repository, nfce_disabler, order_taker)
        order_disabler.disable_all_orders()

        nfce_disabler.disable_fiscal_number.assert_called()
        order = nfce_disabler.disable_fiscal_number.call_args[0][0]
        self.assertEqual(eTree.tostring(order), eTree.tostring(eTree.XML(order_xml)))

    def test_singleOrderIdReturned_markOrderDisabledCalledWithCorrectOrderIdAndPosId(self):
        order_repository = self._aOrderRepositoryReturning([OrderKey("1", "13")])
        nfce_disabler = self._aNfceDisabler().build()
        order_xml = "<order></order>"
        order_taker = self._aOrderTaker().with_return_value(order_xml).build()

        order_taker.get_order_picture = mock.Mock(return_value=order_xml)

        order_disabler = OrderDisabler(order_repository, nfce_disabler, order_taker)
        order_disabler.disable_all_orders()

        order_repository.mark_order_disabled.assert_called_with("1", "13")

    def test_noOrderIdReturned_noOrderPictureNeitherDisableFiscalNumberCalled(self):
        order_repository = self._aOrderRepositoryReturning([])
        order_taker = self._aOrderTaker().build()
        nfce_disabler = self._aNfceDisabler().build()

        order_disabler = OrderDisabler(order_repository, nfce_disabler, order_taker)
        order_disabler.disable_all_orders()

        nfce_disabler.disable_fiscal_number.assert_not_called()
        order_taker.get_order_picture.assert_not_called()

    def test_twoOrderIdsReturnedExceptionOnFirst_SecondOrderStillDisabled(self):
        order_repository = self._aOrderRepositoryReturning([OrderKey("1", "1"), OrderKey("1", "2")])
        order_taker = self._aOrderTaker().with_side_effect(["<order1></order1>", "<order2></order2>"]).build()
        nfce_disabler = self._aNfceDisabler().with_side_effect(self._exception_on_order1).build()

        order_disabler = OrderDisabler(order_repository, nfce_disabler, order_taker)
        order_disabler.disable_all_orders()

        nfce_disabler.disable_fiscal_number.assert_called()
        order = nfce_disabler.disable_fiscal_number.call_args[0][0]
        self.assertEqual(eTree.tostring(order), eTree.tostring(eTree.XML("<order2></order2>")))

    def test_twoOrderIdsReturnedExceptionOnFirst_SecondOrderStillMarkAsDisabled(self):
        order_repository = self._aOrderRepositoryReturning([OrderKey("1", "1"), OrderKey("1", "2")])
        order_taker = self._aOrderTaker().with_side_effect(["<order1></order1>", "<order2></order2>"]).build()
        nfce_disabler = self._aNfceDisabler().with_side_effect(self._exception_on_order1).build()

        order_disabler = OrderDisabler(order_repository, nfce_disabler, order_taker)
        order_disabler.disable_all_orders()

        order_repository.mark_order_disabled.assert_called_with("1", "2")

    def test_twoOrderIdsReturnedExceptionOnFirst_MarkOrderNotDisabledCalledOnFirts(self):
        order_repository = self._aOrderRepositoryReturning([OrderKey("1", "1"), OrderKey("1", "2")])
        order_taker = self._aOrderTaker().with_side_effect(["<order1></order1>", "<order2></order2>"]).build()
        nfce_disabler = self._aNfceDisabler().with_side_effect(self._exception_on_order1).build()

        order_disabler = OrderDisabler(order_repository, nfce_disabler, order_taker)
        order_disabler.disable_all_orders()

        order_repository.mark_order_not_disabled.assert_called_with("1", "1")

    def test_invalidXmlReturned_MarkOrderNotDisabledCalled(self):
        order_repository = self._aOrderRepositoryReturning([OrderKey("1", "1")])
        order_taker = self._aOrderTaker().with_return_value("ag4aregae").build()
        nfce_disabler = self._aNfceDisabler().build()

        order_disabler = OrderDisabler(order_repository, nfce_disabler, order_taker)
        order_disabler.disable_all_orders()

        order_repository.mark_order_not_disabled.assert_called_with("1", "1")

    def test_ConnectionExceptionWithSefaz_OrderNotMarkedAsNotDisabled(self):
        order_repository = self._aOrderRepositoryReturning([OrderKey("1", "1")])
        order_taker = self._aOrderTaker().with_side_effect(["<order1></order1>"]).build()
        nfce_disabler = self._aNfceDisabler().with_side_effect(RequestException).build()

        order_disabler = OrderDisabler(order_repository, nfce_disabler, order_taker)
        order_disabler.disable_all_orders()

        order_repository.mark_order_disabled.assert_not_called()
        order_repository.mark_order_not_disabled.assert_not_called()
        
    def test_ConnectionExceptionWithSefaz_OrderNotMarkedAsNotDisabled(self):
        order_repository = self._aOrderRepositoryReturning([OrderKey("1", "1")])
        order_taker = self._aOrderTaker().with_side_effect(["<order1></order1>"]).build()
        nfce_disabler = self._aNfceDisabler().with_side_effect(Exception).build()

        order_disabler = OrderDisabler(order_repository, nfce_disabler, order_taker)
        order_disabler.disable_all_orders()

        order_repository.mark_order_disabled.assert_not_called()
        order_repository.mark_order_not_disabled.assert_called_with("1", "1")

    def _aOrderRepositoryReturning(self, value):
        order_repository = mock.NonCallableMagicMock(spec=OrderRepository)
        order_repository.get_all_orders_to_disable = mock.Mock(return_value=value)
        order_repository.mark_order_disabled = mock.Mock()
        order_repository.mark_order_not_disabled = mock.Mock()
        return order_repository

    def _aOrderTakerWithSideEffect(self, side_effect):
        order_taker = mock.NonCallableMagicMock(spec=OrderTaker)
        order_taker.get_order_picture = mock.Mock(side_effect=side_effect)
        return order_taker

    def _aNfceDisablerWithSideEffect(self, side_effect):
        nfce_disabler = mock.NonCallableMagicMock(spec=NfceDisabler)
        nfce_disabler.disable_fiscal_number = mock.Mock(side_effect=side_effect)

    def _exception_on_order1(sefl, arg):
        if eTree.tostring(arg) == eTree.tostring(eTree.XML("<order1></order1>")):
            raise Exception("Error disabling order")

    def _aOrderTaker(self):
        return OrderTakerBuilder()

    def _aNfceDisabler(self):
        return NfceDisablerBuilder()
    
    def _aOrderRepository(self):
        return OrderRepositoryBuilder()


class OrderRepositoryBuilder(object):
    def __init__(self):
        self.return_orders = None
        
    def with_return_orders(self, return_orders):
        self.return_orders = return_orders
        return self
    
    def build(self):
        order_repository = mock.NonCallableMagicMock(spec=OrderRepository)
        order_repository.get_all_order_to_disable = mock.Mock()
        if self.return_orders is not None:
            order_repository.get_all_order_to_disable.return_value = self.return_orders
        
        
class NfceDisablerBuilder(object):
    def __init__(self):
        self.side_effect = None

    def with_side_effect(self, side_effect):
        self.side_effect = side_effect
        return self

    def build(self):
        nfce_disabler = mock.NonCallableMagicMock(spec=NfceDisabler)
        nfce_disabler.disable_fiscal_number = mock.Mock()

        if self.side_effect is not None:
            nfce_disabler.disable_fiscal_number.side_effect = self.side_effect

        return nfce_disabler


class OrderTakerBuilder(object):
    def __init__(self):
        self.side_effect = None
        self.return_value = None

    def with_return_value(self, return_value):
        self.return_value = return_value
        return self

    def with_side_effect(self, side_effect):
        self.side_effect = side_effect
        return self

    def build(self):
        order_taker = mock.NonCallableMagicMock(spec=OrderTaker)
        order_taker.get_order_picture = mock.Mock()

        if self.side_effect is not None:
            order_taker.get_order_picture.side_effect = self.side_effect

        return order_taker

def aOrderTaker():
    return OrderTakerBuilder()
