import unittest
import mock
from remoteorder import RemoteOrderTaker, OrderTakerWrapper, RemoteOrderItemCreator
from remoteorder.model import RemoteOrder, PickUpInfo
from remoteorder.repository import OrderRepository


class SaveRemoteOrderTestCase(unittest.TestCase):
    def __init__(self, method_name):
        super(SaveRemoteOrderTestCase, self).__init__(method_name)
        self.order_taker_wrapper = mock.NonCallableMagicMock(spec=OrderTakerWrapper)
        self.order_item_creator = mock.NonCallableMagicMock(spec=RemoteOrderItemCreator)
        self.order_repository = mock.NonCallableMagicMock(spec=OrderRepository)

        self.remote_order_taker = RemoteOrderTaker(1, self.order_taker_wrapper, self.order_item_creator, self.order_repository)

    def test_MethodCalled_CheckBusinessDayIsCalled(self):
        remote_order = RemoteOrder()
        remote_order.pickup = PickUpInfo()
        remote_order.pickup.company = "company"
        self.remote_order_taker.save_remote_order(remote_order, [])

        self.order_taker_wrapper.check_business_period.assert_called_with(1)

    def test_ExceptionOnCheckBusinessPeriod_ExceptionIsRaised(self):
        remote_order = RemoteOrder()
        remote_order.pickup = PickUpInfo()
        remote_order.pickup.company = "company"

        raised_exception = Exception("exception")
        self.order_taker_wrapper.check_business_period = mock.Mock(side_effect=raised_exception)

        try:
            self.remote_order_taker.save_remote_order(remote_order, [])
            self.fail()
        except Exception as ex:
            self.assertEqual(ex, raised_exception)

    def test_MethodCalled_CreateOrderCalledWithRemoteOrder(self):
        remote_order = RemoteOrder()
        self.remote_order_taker.save_remote_order(remote_order, [])

        self.order_taker_wrapper.create_order.assert_called_with(1, remote_order)

    def test_ExceptionInCreateOrder_ExceptionRaised(self):
        raised_exception = Exception("exception")
        self.order_taker_wrapper.create_order = mock.Mock(side_effect=raised_exception)

        remote_order = RemoteOrder()
        remote_order.pickup = PickUpInfo()
        remote_order.pickup.company = ""
        not_used_composition_tree = None

        try:
            self.remote_order_taker.save_remote_order(remote_order, not_used_composition_tree)
            self.fail()
        except Exception as ex:
            self.assertEqual(ex, raised_exception)

    def test_OrderSuccessfulyCreated_CreateCurrentOrderItemsCalled(self):
        self.order_taker_wrapper.create_order = mock.Mock(return_value=1)

        remote_order = RemoteOrder()
        remote_order.pickup = PickUpInfo()
        remote_order.pickup.company = ""
        order_tress = []

        self.remote_order_taker.save_remote_order(remote_order, order_tress)
        self.order_item_creator.create_current_order_items.assert_called_with(1, 1, order_tress)

    def test_OrderSuccessfulyCreated_OrderIdReturned(self):
        self.order_taker_wrapper.create_order = mock.Mock(return_value=1)

        remote_order = RemoteOrder()
        remote_order.pickup = PickUpInfo()
        remote_order.pickup.company = ""
        order_tress = []

        order_id = self.remote_order_taker.save_remote_order(remote_order, order_tress)
        self.assertEqual(order_id, 1)


    def test_ExceptionInCreateCurrentOrderItems_ExceptionRaised(self):
        raised_exception = Exception("exception")
        self.order_item_creator.create_current_order_items = mock.Mock(side_effect=raised_exception)

        remote_order = RemoteOrder()
        remote_order.pickup = PickUpInfo()
        remote_order.pickup.company = ""
        order_tress = []

        try:
            self.remote_order_taker.save_remote_order(remote_order, order_tress)
            self.fail()
        except Exception as ex:
            self.assertEqual(ex, raised_exception)

    def test_CurrentOrderItemsCreated_SaveOrderCalled(self):
        self.order_taker_wrapper.create_order = mock.Mock(return_value=10)

        remote_order = RemoteOrder()
        remote_order.pickup = PickUpInfo()
        remote_order.pickup.company = ""
        order_tress = []

        self.remote_order_taker.save_remote_order(remote_order, order_tress)

        self.order_taker_wrapper.save_order.assert_called_with(1)

    def test_ExceptionSavingOrder_ExceptionRaised(self):
        raised_exception = Exception("exception")
        self.order_taker_wrapper.save_order = mock.Mock(side_effect=raised_exception)
        remote_order = RemoteOrder()
        remote_order.pickup = PickUpInfo()
        remote_order.pickup.company = ""
        order_tress = []

        try:
            self.remote_order_taker.save_remote_order(remote_order, order_tress)
            self.fail()
        except Exception as ex:
            self.assertEqual(ex, raised_exception)
