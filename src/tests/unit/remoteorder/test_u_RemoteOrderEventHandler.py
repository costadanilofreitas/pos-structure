import unittest
import mock

from RemoteOrderEventHandler import RemoteOrderEventHandler
from remoteorder.model import Event, ProcessedOrder
from remoteorder import RemoteOrderProcessor
from msgbus import MBEasyContext
from bustoken import TK_REMOTE_ORDER_GET_STORED_ORDERS, TK_REMOTE_ORDER_SEND_ORDER_TO_PRODUCTION, TK_REMOTE_ORDER_GET_STORE, TK_REMOTE_ORDER_OPEN_STORE, TK_REMOTE_ORDER_CLOSE_STORE


class GetHandledTokensTestCase(unittest.TestCase):
    def test_correctListOfTokensAreReturned(self):
        event_handler = RemoteOrderEventHandler(None, None, None, None, None)
        ret = event_handler.get_handled_tokens()

        self.assertEqual(len(ret), 5)
        self.assertTrue(TK_REMOTE_ORDER_GET_STORED_ORDERS in ret)
        self.assertTrue(TK_REMOTE_ORDER_SEND_ORDER_TO_PRODUCTION in ret)
        self.assertTrue(TK_REMOTE_ORDER_GET_STORE in ret)
        self.assertTrue(TK_REMOTE_ORDER_OPEN_STORE in ret)
        self.assertTrue(TK_REMOTE_ORDER_CLOSE_STORE in ret)
        self.assertTrue(TK_REMOTE_ORDER_GET_STORED_ORDERS in ret)


class HandleMessageTestCase(unittest.TestCase):
    def test_NotImplementedErrorRaised(self):
        event_handler = RemoteOrderEventHandler(None, None)

        try:
            event_handler.handle_message(None)
            self.fail()
        except NotImplementedError as ex:
            pass


class TerminateEventTestCase(unittest.TestCase):
    def test_NoErrors(self):
        event_handler = RemoteOrderEventHandler(None, None, None, None, None)
        event_handler.terminate_event()


class HandleEventTestCase(unittest.TestCase):
    def test_InvalidEvent_NoErrors(self):
        event_handler = RemoteOrderEventHandler(None, None)
        event_handler.handle_event("INVALID_EVENT", "TYPE", "", None)

    def test_OrderReleaseEvent_ProcessRemoteOrderCalledWithData(self):
        remote_order_processor = mock.NonCallableMagicMock(spec=RemoteOrderProcessor)
        remote_order_processor.process_order = mock.Mock()

        mbcontext = mock.NonCallableMagicMock(spec=MBEasyContext)
        event_handler = RemoteOrderEventHandler(mbcontext, remote_order_processor)

        order_json = "{}"
        event_handler.handle_event(Event.LogisticOrderConfirm, "", order_json, None)
        remote_order_processor.process_order.assert_called_with(order_json)

    def test_OrderReleaseEventExceptionFromRemoteOrderProcessor_POSErrorInOrder(self):
        remote_order_processor = mock.NonCallableMagicMock(spec=RemoteOrderProcessor)
        raised_exception = Exception("Exception")
        remote_order_processor.process_order = mock.Mock(side_effect=raised_exception)

        mbcontext = mock.NonCallableMagicMock(spec=MBEasyContext)
        mbcontext.MB_EvtSend = mock.Mock()

        event_handler = RemoteOrderEventHandler(mbcontext, remote_order_processor)

        order_json = "{}"
        event_handler.handle_event(Event.LogisticOrderConfirm, "", order_json, None)

        mbcontext.MB_EasyEvtSend.assert_called_with(Event.PosOrderCancel, "", repr(raised_exception).encode("utf-8"))

    def test_OrderReleaseEventSuccessfulyProcessed_POSOrderConfirmed(self):
        remote_order_processor = mock.NonCallableMagicMock(spec=RemoteOrderProcessor)
        processed_order = ProcessedOrder(123, 456)
        remote_order_processor.process_order = mock.Mock(return_value=processed_order)

        mbcontext = mock.NonCallableMagicMock(spec=MBEasyContext)
        event_handler = RemoteOrderEventHandler(mbcontext, remote_order_processor)

        order_json = "{}"
        event_handler.handle_event(Event.LogisticOrderConfirm, "", order_json, None)
        mbcontext.MB_EasyEvtSend.assert_called_with(Event.PosOrderConfirm, "", """{"local_order_id": 456, "remote_order_id": 123}""")
