from behave import *
from taxcalculator import TaxItemFormatter
from taxcalculator.model import TaxItem
from robber import expect


@given("the tax_item is None")
def step_impl(context):
    context.tax_item = None


@given("the tax_item is valid")
def step_impl(context):
    context.tax_item = TaxItem()
    context.tax_item.line_number = 1
    context.tax_item.level = 0
    context.tax_item.part_code = 1050
    context.tax_item.item_id = "1"

    context.tax_item.quantity = 2
    context.tax_item.unit_price = 23.9
    context.tax_item.item_price = 47.8

    context.tax_item.tax_rule_id = "PIS_10"
    context.tax_item.tax_name = "PIS"
    context.tax_item.tax_index = "PIS"
    context.tax_item.base_amount_bd = 23.9
    context.tax_item.base_amount_ad = 20.9
    context.tax_item.tax_amount_bd = 2.39
    context.tax_item.tax_amount_ad = 2.09
    context.tax_item.tax_included = 0
    context.tax_item.tax_rate = 0.1


@when("the format_tax_item method is called")
def step_impl(context):
    tax_item_formatter = TaxItemFormatter()
    try:
        context.formatted_tax_item = tax_item_formatter.format_tax_item(context.tax_item)
    except Exception as ex:
        context.exception = ex


@then("an Exception from the format_tax_item method is raised")
def step_impl(context):
    if not hasattr(context, 'exception'):
        raise Exception("An exception should have been raised")

    expect(context.exception).to.be.instanceof(Exception)


@then("the returned value is the correct representation of the TaxItem")
def step_impl(context):
    if hasattr(context, 'exception'):
        raise context.exception

    expect(context.formatted_tax_item).to.be.instanceof(str)
    expect(context.formatted_tax_item).to.eq("<TaxItem lineNumber=\"1\" "
                                             "level=\"0\" "
                                             "itemId=\"1\" "
                                             "partCode=\"1050\" "
                                             "taxRuleId=\"PIS_10\" "
                                             "taxName=\"PIS\" "
                                             "taxIndex=\"PIS\" "
                                             "baseAmountBD=\"23.9\" "
                                             "taxAmountBD=\"2.39\" "
                                             "baseAmountAD=\"20.9\" "
                                             "taxAmountAD=\"2.09\" "
                                             "taxIncluded=\"0\" "
                                             "quantity=\"2\" "
                                             "unitPrice=\"23.9\" "
                                             "itemPrice=\"47.8\" "
                                             "taxRate=\"0.1\"/>")
