# encoding: utf-8
import unittest
import mock


from remoteorder import RemoteOrderProcessor, RemoteOrderParser, RemoteOrderValidator, RemoteOrderTaker, StoreService, ProcessedOrderBuilder
from remoteorder.model import RemoteOrder, Store, StoreClosedException, ProcessedOrder


class ProcessOrderTestCase(unittest.TestCase):
    def __init__(self, methodName):
        super(ProcessOrderTestCase, self).__init__(methodName)
        self.remote_order_parser = mock.NonCallableMagicMock(spec=RemoteOrderParser)
        self.remote_order_validator = mock.NonCallableMagicMock(spec=RemoteOrderValidator)
        self.remote_order_taker = mock.NonCallableMagicMock(spec=RemoteOrderTaker)
        self.store_service = mock.NonCallableMagicMock(spec=StoreService)
        open_store = Store()
        open_store.status = "Open"
        self.store_service.get_store = mock.Mock(return_value=open_store)
        self.remote_order_taker.get_local_order_id = mock.Mock(return_value=None)
        self.processed_order_builder = mock.NonCallableMagicMock(spec=ProcessedOrderBuilder)

        self.remote_order_processor = RemoteOrderProcessor(self.remote_order_parser, self.remote_order_validator, self.remote_order_taker, self.store_service,
                                                           self.processed_order_builder)

    def test_NewRemoteOrderJson_JsonIsSentToRemoteOrderParser(self):
        self.remote_order_parser.parse_order = mock.Mock()

        input_json = "{}"
        self.remote_order_processor.process_order(input_json)
        self.remote_order_parser.parse_order.assert_called_with(input_json)

    def test_OrderThatRaisesExceptionFromParser_ExceptionFromParserIsReraised(self):
        expected_exception = Exception("exception")
        self.remote_order_parser.parse_order = mock.Mock(side_effect=expected_exception)

        try:
            self.remote_order_processor.process_order("{}")
        except Exception as ex:
            self.assertEqual(ex, expected_exception)

    def test_NewOrder_RemoteOrderFromParserIsPassedToValidator(self):
        remote_order = RemoteOrder()
        remote_order.id = 1234
        self.remote_order_parser.parse_order = mock.Mock(return_value=remote_order)

        input_json = "{}"
        self.remote_order_processor.process_order(input_json)
        self.remote_order_validator.validate_order.assert_called_with(remote_order)

    def test_AnyJsonExceptionFromOrderValidator_ExceptionFromValidatorIsReraised(self):
        raised_exception = Exception("exception")
        self.remote_order_validator.validate_order = mock.Mock(side_effect=raised_exception)

        try:
            input_json = "{}"
            self.remote_order_processor.process_order(input_json)
        except Exception as ex:
            self.assertEqual(ex, raised_exception)

    def test_ValidNewRemoteOrder_CompleteOrderIsPassedToRemoteOrderTaker(self):
        remote_order = RemoteOrder()
        remote_order.id = 1234
        self.remote_order_parser.parse_order = mock.Mock(return_value=remote_order)
        order_tress = "order_tress"
        self.remote_order_validator.validate_order = mock.Mock(return_value=order_tress)
        self.remote_order_taker.save_remote_order = mock.Mock(return_value=456)

        input_json = "{}"
        self.remote_order_processor.process_order(input_json)
        self.remote_order_taker.save_remote_order.assert_called_with(remote_order, order_tress)

    def test_AnyJsonExceptionInRemoteOrderTaker_ExceptionFromRemoteOrderTakerIsReraised(self):
        raised_exception = Exception("exception")
        self.remote_order_taker.save_remote_order = mock.Mock(side_effect=raised_exception)

        try:
            input_json = "{}"
            self.remote_order_processor.process_order(input_json)
        except Exception as ex:
            self.assertEqual(ex, raised_exception)

    def test_JsonOfNewOrder_ProcessedOrderFromProcessedOrderBuilderIsReturned(self):
        remote_order = RemoteOrder()
        remote_order.id = 1234
        self.remote_order_parser.parse_order = mock.Mock(return_value=remote_order)
        self.remote_order_taker.save_remote_order = mock.Mock(return_value=456)
        mock_processed_order = ProcessedOrder(10, 100, [])
        self.processed_order_builder.build_processed_order = mock.Mock(return_value=mock_processed_order)

        input_json = "{}"
        processed_order = self.remote_order_processor.process_order(input_json)
        self.assertEqual(processed_order, mock_processed_order)

    def test_ValidJsonStoreClosed_StoreClosedException(self):
        remote_order = RemoteOrder()
        remote_order.id = 1234
        self.remote_order_parser.parse_order = mock.Mock(return_value=remote_order)

        closed_store = Store()
        closed_store.status = "Closed"
        self.store_service.get_store = mock.Mock(return_value=closed_store)

        input_json = "{}"
        try:
            processed_order = self.remote_order_processor.process_order(input_json)
            self.fail()
        except StoreClosedException as ex:
            pass

    def test_RemoteOrderAlreadyInPos_ProcessedOrderReturned(self):
        remote_order = RemoteOrder()
        remote_order.id = 1234
        self.remote_order_parser.parse_order = mock.Mock(return_value=remote_order)

        local_order_id = 155
        self.remote_order_taker.get_local_order_id = mock.Mock(return_value=local_order_id)

        mock_processed_order = ProcessedOrder(10, 100, [])
        self.processed_order_builder.build_processed_order = mock.Mock(return_value=mock_processed_order)
        input_json = "{}"
        processed_order = self.remote_order_processor.process_order(input_json)
        self.assertEqual(processed_order, mock_processed_order)
