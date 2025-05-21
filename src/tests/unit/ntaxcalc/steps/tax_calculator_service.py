from behave import *
import mock
from taxcalculator import OrderParser, GeneralTaxCalculator, TaxCalculatorService, OrderFormatter
from taxcalculator.model import Order
from robber import expect


@given("there is a mocked OrderParser")
def step_impl(context):
    context.order_parser = mock.NonCallableMagicMock(spec=OrderParser)
    context.parsed_order = Order()
    context.parsed_order.pos_id = 1
    context.parsed_order.order_id = 10
    context.parsed_order.sale_items = ["sale_item1", "sale_item2"]
    context.order_parser.parse_order = mock.Mock(return_value=context.parsed_order)


@given("there is a mocked OrderParser that raised an Exception")
def step_impl(context):
    context.order_parser = mock.NonCallableMagicMock(spec=OrderParser)
    context.order_parser_exception = Exception("OrderParserException")
    context.order_parser.parse_order = mock.Mock(side_effect=context.order_parser_exception)


@given("there is a mocked GeneralTaxCalculator")
def step_impl(context):
    context.general_tax_calculator = mock.NonCallableMagicMock(spec=GeneralTaxCalculator)
    context.all_taxes = [1, 2]
    context.general_tax_calculator.calculate_all_taxes = mock.Mock(return_value=context.all_taxes)


@given("there is a mocked OrderFormatter")
def step_impl(context):
    context.order_formatter = mock.NonCallableMagicMock(spec=OrderFormatter)
    context.order_formatter.format_order = mock.Mock(return_value="formated_order")


@given("there is a mocked GeneralTaxCalculator that raises an Exception")
def step_impl(context):
    context.general_tax_calculator = mock.NonCallableMagicMock(spec=GeneralTaxCalculator)
    context.tax_calculator_exception = Exception("TaxCalculatorException")
    context.general_tax_calculator.calculate_all_taxes = mock.Mock(side_effect=context.tax_calculator_exception)


@when("the calculate_taxes method is called")
def step_impl(context):
    tax_calculator_service = TaxCalculatorService(context.order_parser, context.general_tax_calculator, context.order_formatter)
    context.order = "my_order"
    try:
        context.formatted_order = tax_calculator_service.calculate_taxes(context.order)
    except Exception as ex:
        context.exception = ex


@then("the parse_order method of the OrderParsed is called with the received order")
def step_impl(context):
    context.order_parser.parse_order.assert_called_with(context.order)


@then("the calculate_all_taxes method of the GeneralTaxCalculator is called with every SaleItem returned from the OrderParser")
def step_impl(context):
    expect(len(context.general_tax_calculator.calculate_all_taxes.mock_calls)).to.eq(2)
    context.general_tax_calculator.calculate_all_taxes.assert_has_calls([mock.call("sale_item1"), mock.call("sale_item2")])


@then("the order is passed to the OrderFormatter with the tax_items property filled with the calculated taxes")
def step_impl(context):
    expect(context.parsed_order.tax_items).to.be.instanceof(list)
    expect(len(context.parsed_order.tax_items)).to.eq(4)
    expect(context.parsed_order.tax_items[0]).to.eq(1)
    expect(context.parsed_order.tax_items[1]).to.eq(2)
    expect(context.parsed_order.tax_items[2]).to.eq(1)
    expect(context.parsed_order.tax_items[3]).to.eq(2)

    context.order_formatter.format_order.assert_called_with(context.parsed_order)


@then("the return value is equal to the value returned from the OrderFormatter")
def step_impl(context):
    expect(context.formatted_order).be.eq("formated_order")


@then("the exception risen from the OrderParser is raised by the TaxCalculatorService")
def step_impl(context):
    if not hasattr(context, 'exception'):
        raise Exception("An exception should have been raised")

    expect(context.exception).to.be.instanceof(Exception)


