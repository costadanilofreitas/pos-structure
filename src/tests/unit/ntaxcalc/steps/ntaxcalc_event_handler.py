from behave import *
import mock
from taxcalculator import TaxCalculatorService
from eventhandler import NTaxCalcEventHandler
from msgbus import MBEasyContext, TK_SYS_NAK, FM_STRING
from msgbusmock import FakeMessage
from robber import expect


@given("there is a mocked tax_calculator_service")
def step_impl(context):
    context.tax_calculator_service = mock.NonCallableMagicMock(spec=TaxCalculatorService)
    context.tax_calculator_service.calculate_taxes = mock.Mock(return_value="calculate_tax_response")


@given("there is a mocked tax_calculator_service that raises an Exception")
def step_impl(context):
    context.tax_calculator_service = mock.NonCallableMagicMock(spec=TaxCalculatorService)
    context.tax_calculator_service.calculate_taxes = mock.Mock(side_effect=Exception("CalculateTaxesEcetpion"))


@given("there is a mocked MBContext")
def step_impl(context):
    context.mbcontext = mock.NonCallableMagicMock(spec=MBEasyContext)
    context.mbcontext.MB_ReplyMessage = mock.Mock()


@given("an invalid subject will be called")
def step_impl(context):
    context.subject = "INVALID"
    context.data = None


@given("an TAX_CALC subject will be called")
def step_impl(context):
    context.subject = "TAX_CALC"
    context.data = "event_data"


@given("there is a mocked logger")
def step_impl(context):
    import eventhandler
    eventhandler.logger = mock.NonCallableMagicMock()
    eventhandler.logger.exception = mock.Mock()


@when("the handle_event method is called")
def step_impl(context):
    event_handler = NTaxCalcEventHandler(context.mbcontext, context.tax_calculator_service)
    context.msg = FakeMessage(0, "")
    event_handler.handle_event(context.subject, None, context.data, context.msg)


@then("there are no calls on the calculate_tax method")
def step_impl(context):
    context.mbcontext.assert_not_called()


@then("the calculate_taxes is called with the data of the event")
def step_impl(context):
    context.tax_calculator_service.calculate_taxes.assert_called_with(context.data)


@then("the response from calculate_taxes is replied to the message bus")
def step_impl(context):
    context.mbcontext.MB_ReplyMessage.assert_called_with(context.msg, data="calculate_tax_response", format=FM_STRING)


@then("an NACK is sent on the message bus")
def step_impl(context):
    expect(context.msg.token).be.eq(TK_SYS_NAK)
    context.mbcontext.MB_ReplyMessage.assert_called_with(context.msg)


@then("the exception is logged")
def step_impl(context):
    import eventhandler
    eventhandler.logger.exception.assert_called()
