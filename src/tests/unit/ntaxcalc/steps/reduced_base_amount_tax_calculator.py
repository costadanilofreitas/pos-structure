from behave import *
from taxcalculator.model import SaleItem, TaxItem
from taxcalculator import ReducedBaseAmountTaxCalculator
from robber import expect


@given("there is a ReducedBaseAmountTaxCalculator created with rate = 10% and taxes_to_reduce = ['ICMS']")
def step_impl(context):
    context.reduced_base_tax_calculator = ReducedBaseAmountTaxCalculator("PIS_10", "PIS", "13", 0.1, {1050: 1050}, ["ICMS"])


@when("the calculate_tax method is called with a SaleItem with a item_price = 23.90 , quantity = 1 and a previous taxes with ICMS value of 0.15")
def step_impl(context):
    context.sale_item = SaleItem(0, 0, 1050, None, 23.9, 1, 23.9, 0.0)
    previsou_tax_item = TaxItem()
    previsou_tax_item.tax_name = "ICMS"
    previsou_tax_item.tax_amount_ad = previsou_tax_item.tax_amount_bd = 0.15
    context.tax_item = context.reduced_base_tax_calculator.calculate_tax(context.sale_item, [(None, previsou_tax_item)])


@then("the TaxItem returned has tax_amount_bd and tax_amouint_ad = 2.375 and base_amount_db and base_amount_ad = 23.75")
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
    expect(tax_item.base_amount_bd).to.eq(23.75)
    expect(tax_item.base_amount_ad).to.eq(23.75)
    expect(tax_item.tax_amount_ad).to.eq(2.375)
    expect(tax_item.tax_amount_bd).to.eq(2.375)
    expect(tax_item.tax_rule_id).to.eq("PIS_10")
    expect(tax_item.tax_index).to.eq("13")
    expect(tax_item.tax_name).to.eq("PIS")

