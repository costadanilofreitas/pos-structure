from behave import *
from taxcalculator.model import SaleItem, TaxItem
from taxcalculator import FixedRateTaxCalculator
from robber import expect


@given("there is a FixedTaxCalculator with the tax value of 10% created")
def step_impl(context):
    context.fixed_tax_calculator = FixedRateTaxCalculator("PIS_10", "PIS", "13", 0.1, {1050: 1050})


@when("the calculate_tax method is called with a SaleItem with a item_price = 23.90 , quantity = 1")
def step_impl(context):
    context.sale_item = SaleItem(0, 0, 1050, None, 23.9, 1, 23.9)
    context.tax_item = context.fixed_tax_calculator.calculate_tax(context.sale_item, [])


@when("the calculate_tax method is called with with a SaleItem with a item_price = 23.90, item_discount = 2.39, quantity = 1")
def step_impl(context):
    context.sale_item = SaleItem(0, 0, 1050, None, 23.9, 1, 23.9, 0.0, 2.39, 2.39)
    context.tax_item = context.fixed_tax_calculator.calculate_tax(context.sale_item, [])


@when("the calculate_tax method is called with a not registered SaleItem with a item_price = 10.90 , quantity = 1")
def step_impl(context):
    context.sale_item = SaleItem(0, 0, 9012, None, 10.9, 1, 10.9)
    context.tax_item = context.fixed_tax_calculator.calculate_tax(context.sale_item, [])


@when("the calculate_tax method is called with SaleItem with a item_price = 10.90 , quantity = 3")
def step_impl(context):
    context.sale_item = SaleItem(0, 0, 1050, None, 32.7, 3, 10.9)
    context.tax_item = context.fixed_tax_calculator.calculate_tax(context.sale_item, [])


@when("the calculate_tax method is called with None")
def step_impl(context):
    try:
        context.tax_item = context.fixed_tax_calculator.calculate_tax(None, [])
    except Exception as ex:
        context.exception = ex


@then("the ItemTax returned has tax_amount_bd and tax_amouint_ad = 2.39 and base_amount_db and base_amount_ad = 23.9")
def step_impl(context):
    tax_item = context.tax_item  # type: TaxItem
    expect(tax_item.line_number).to.eq(0)
    expect(tax_item.level).to.eq(0)
    expect(tax_item.item_id).to.be.none()
    expect(tax_item.part_code).to.eq(1050)
    expect(tax_item.quantity).to.eq(1)
    expect(tax_item.unit_price).to.eq(23.9)
    expect(tax_item.item_price).to.eq(23.9)

    expect(tax_item.tax_rate).to.eq(0.1)
    expect(tax_item.base_amount_bd).to.eq(23.9)
    expect(tax_item.base_amount_ad).to.eq(23.9)
    expect(tax_item.tax_amount_ad).to.eq(2.39)
    expect(tax_item.tax_amount_bd).to.eq(2.39)
    expect(tax_item.tax_rule_id).to.eq("PIS_10")
    expect(tax_item.tax_index).to.eq("13")
    expect(tax_item.tax_name).to.eq("PIS")


@then("the ItemTax returned has tax_amount_bd and tax_amount_ad = 2.151 and base_amount_db = 23.9 and base_amount_ad = 21.51")
def step_impl(context):
    tax_item = context.tax_item  # type: TaxItem
    expect(tax_item.line_number).to.eq(0)
    expect(tax_item.level).to.eq(0)
    expect(tax_item.item_id).to.be.none()
    expect(tax_item.part_code).to.eq(1050)
    expect(tax_item.quantity).to.eq(1)
    expect(tax_item.unit_price).to.eq(23.9)
    expect(tax_item.item_price).to.eq(23.9)

    expect(tax_item.tax_rate).to.eq(0.1)
    expect(tax_item.base_amount_bd).to.eq(23.9)
    expect(round(tax_item.base_amount_ad, 2)).to.eq(21.51)
    expect(round(tax_item.tax_amount_ad, 3)).to.eq(2.151)
    expect(tax_item.tax_amount_bd).to.eq(2.39)
    expect(tax_item.tax_rule_id).to.eq("PIS_10")
    expect(tax_item.tax_index).to.eq("13")
    expect(tax_item.tax_name).to.eq("PIS")


@then("the ItemTax returned has tax_amount_bd and tax_amouint_ad = 3.27 and base_amount_db and base_amount_ad = 32.7")
def step_impl(context):
    tax_item = context.tax_item  # type: TaxItem
    expect(tax_item.line_number).to.eq(0)
    expect(tax_item.level).to.eq(0)
    expect(tax_item.item_id).to.be.none()
    expect(tax_item.part_code).to.eq(1050)
    expect(tax_item.quantity).to.eq(3)
    expect(tax_item.unit_price).to.eq(10.9)
    expect(tax_item.item_price).to.eq(32.7)

    expect(tax_item.tax_rate).to.eq(0.1)
    expect(tax_item.base_amount_bd).to.eq(32.7)
    expect(tax_item.base_amount_ad).to.eq(32.7)
    expect(tax_item.tax_amount_ad).to.eq(3.27)
    expect(tax_item.tax_amount_bd).to.eq(3.27)
    expect(tax_item.tax_rule_id).to.eq("PIS_10")
    expect(tax_item.tax_index).to.eq("13")
    expect(tax_item.tax_name).to.eq("PIS")


@then("None is returned")
def step_impl(context):
    expect(context.tax_item).to.be.none()


@then("an Exception is risen")
def step_impl(context):
    if not hasattr(context, "exception"):
        raise Exception("an Exception should be risen")

    expect(context.exception).to.be.instanceof(Exception)
