import unittest
import mock

from remoteorder.model import RemoteOrder, OrderItem
from remoteorder.compositiontree import CompositionTreeBuilder
from remoteorder import CompositionTreeValidator, RemoteOrderValidator, OrderValidationException, OrderValidationError, OrderPriceCalculator, WarningEmitter


class ValidateOrderTestCase(unittest.TestCase):
    def __init__(self, methodName):
        super(ValidateOrderTestCase, self).__init__(methodName)
        self.composition_tree_builder = mock.NonCallableMagicMock(spec=CompositionTreeBuilder)
        self.composition_validator = mock.NonCallableMagicMock(spec=CompositionTreeValidator)
        self.order_price_calculator = mock.NonCallableMagicMock(spec=OrderPriceCalculator)
        self.warning_emitter = mock.NonCallableMagicMock(spec=WarningEmitter)

        self.remote_order_validator = RemoteOrderValidator(self.composition_tree_builder, self.composition_validator, self.order_price_calculator, self.warning_emitter)

    def test_OrderWithNoItems_OrderValidationExceptionRaised(self):
        remote_order = RemoteOrder()
        remote_order.items = []

        try:
            self.remote_order_validator.validate_order(remote_order)
            self.fail()
        except OrderValidationException as ex:
            self.assertEqual(ex.order_validation_error, OrderValidationError.OrderWithNoItens)

    def test_OrderWithItemsNone_OrderValidationExceptionRaised(self):
        remote_order = RemoteOrder()
        remote_order.items = None

        try:
            self.remote_order_validator.validate_order(remote_order)
            self.fail()
        except OrderValidationException as ex:
            self.assertEqual(ex.order_validation_error, OrderValidationError.OrderWithNoItens)

    def test_OrderWithTwoItens_GetCompositionTreeCalledWithEachPartCode(self):
        self.composition_tree_builder.get_composition_tree = mock.Mock()

        remote_order = self._aRemoteOrderWithTwoSimpleItens()

        self.remote_order_validator.validate_order(remote_order)

        self.composition_tree_builder.get_composition_tree.assert_has_calls([mock.call(remote_order.items[0].part_code), mock.call(remote_order.items[1].part_code)])

    def test_OrderWithTwoItens_ValidateOrderCompositionCalledWithEachPartCode(self):
        composition_tree = u"composition_tree"
        self.composition_tree_builder.get_composition_tree = mock.Mock(return_value=composition_tree)

        remote_order = self._aRemoteOrderWithTwoSimpleItens()

        self.remote_order_validator.validate_order(remote_order)

        self.composition_validator.validate_order_composition.assert_has_calls([
            mock.call(composition_tree, remote_order.items[0]),
            mock.call(composition_tree, remote_order.items[1])])

    def test_OrderWithTwoItens_ListWithTwoElementsReturned(self):
        complete_tree = "compltere_tree"
        self.composition_validator.validate_order_composition = mock.Mock(return_value=complete_tree)

        remote_order = self._aRemoteOrderWithTwoSimpleItens()

        complete_order = self.remote_order_validator.validate_order(remote_order)

        self.assertIsNotNone(complete_order)
        self.assertEqual(len(complete_order), 2)
        self.assertEqual(complete_order[0], complete_tree)
        self.assertEqual(complete_order[1], complete_tree)

    def _aRemoteOrderWithTwoSimpleItens(self):
        remote_order = RemoteOrder()

        remote_order.items = []
        item1 = OrderItem()
        item1.part_code = "1050"
        remote_order.items.append(item1)

        item2 = OrderItem()
        item2.part_code = "6012"
        remote_order.items.append(item2)

        return remote_order
