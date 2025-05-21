from behave import *
import mock
from taxcalculator import TaxItemFormatter, OrderFormatter
from taxcalculator.model import Order
from robber import expect
from xml.etree import cElementTree as eTree


@given("there is a mocked TaxItemFormatter")
def step_impl(context):
    context.tax_item_formatter = mock.NonCallableMagicMock(spec=TaxItemFormatter)
    context.tax_item_formatter.format_tax_item = mock.Mock(return_value="tax_item")


@given("there is a mocked Order")
def step_impl(context):
    context.order = Order()
    context.order.order_id = 10
    context.order.pos_id = 1
    context.order.tax_items = ["item1", "item2"]


@when("the format_order method of the OrderFormatter is called")
def step_impl(context):
    order_formatter = OrderFormatter(context.tax_item_formatter)
    context.formatted_order = order_formatter.format_order(context.order)


@then("the format_tax_item is called for every TaxItem")
def step_impl(context):
    expect(len(context.tax_item_formatter.format_tax_item.mock_calls)).be.eq(2)
    context.tax_item_formatter.format_tax_item.assert_has_calls([mock.call("item1"), mock.call("item2")])


@then("the returned formatted order is correct")
def step_impl(context):
    expect(context.formatted_order).be.eq("<Order posId=\"1\" orderId=\"10\">tax_itemtax_item</Order>")
