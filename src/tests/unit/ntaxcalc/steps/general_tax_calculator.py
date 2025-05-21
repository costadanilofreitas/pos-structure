from behave import *
import mock
from taxcalculator import TaxCalculator, GeneralTaxCalculator
from taxcalculator.model import SaleItem, TaxItem
from robber import expect

all_responses = []
tax_calculator_1_previous_taxes = None
tax_calculator_2_previous_taxes = None
tax_calculator_3_previous_taxes = None


@given("there is a GeneralTaxCalculator initialized with three mocked TaxCalculators")
def step_impl(context):
    context.tax_calculator_1 = mock.NonCallableMagicMock(spec=TaxCalculator)
    context.tax_calculator_1.calculate_tax = mock.Mock(side_effect=_tax_calculator_side_effect_1)
    context.tax_calculator_2 = mock.NonCallableMagicMock(spec=TaxCalculator)
    context.tax_calculator_2.calculate_tax = mock.Mock(side_effect=_tax_calculator_side_effect_2)
    context.tax_calculator_3 = mock.NonCallableMagicMock(spec=TaxCalculator)
    context.tax_calculator_3.calculate_tax = mock.Mock(side_effect=_tax_calculator_side_effect_3)
    all_tax_calculators = [context.tax_calculator_1, context.tax_calculator_2, context.tax_calculator_3]
    context.general_tax_calculator = GeneralTaxCalculator(all_tax_calculators)


@given("there is a GeneralTaxCalculator initialized with one TaxCalculator that always returns None")
def step_impl(context):
    context.tax_calculator = mock.NonCallableMagicMock(spec=TaxCalculator)
    context.tax_calculator.calculate_tax = mock.Mock(return_value=None)
    all_tax_calculators = [context.tax_calculator]
    context.general_tax_calculator = GeneralTaxCalculator(all_tax_calculators)


@when("the calculate_tax method is called with a SaleItem")
def step_impl(context):
    context.sale_item = SaleItem(0, 0, 1050, None, 21.9, 1, 21.9)
    context.response = context.general_tax_calculator.calculate_all_taxes(context.sale_item)


@then("all three mocked TaxCalculators are called in order")
def step_impl(context):
    if len(all_responses) != 3:
        raise Exception("All three TaxCalculators should have been called")

    if all_responses[0] != 1 and all_responses[1] != 2 and all_responses[2] != 3:
        raise Exception("The TaxCalculators were called in the incorect order")


@then("the first TaxCalculator must be called with an empty list")
def step_impl(context):
    if not isinstance(tax_calculator_1_previous_taxes, list) or len(tax_calculator_1_previous_taxes) != 0:
        raise Exception("The first tax calculator shoudl be called with an empty list")


@then("the second TaxCalculator must be called with a list with the previous tax calculation")
def step_impl(context):
    if not isinstance(tax_calculator_2_previous_taxes, list) or len(tax_calculator_2_previous_taxes) != 1:
        raise Exception("The first tax calculator shoudl be called with a list with one element")

    if tax_calculator_2_previous_taxes[0][1] != "1":
        raise Exception("The list should have the previous tax calculation")


@then("the third TaxCalculator must be called with a list with the two previous tax calculations")
def step_impl(context):
    if not isinstance(tax_calculator_3_previous_taxes, list) or len(tax_calculator_3_previous_taxes) != 2:
        raise Exception("The first tax calculator shoudl be called with a list with two elements")

    if tax_calculator_3_previous_taxes[0][1] != "1" or tax_calculator_3_previous_taxes[1][1] != "2":
        raise Exception("The list should have the all previous tax calculations")


@then("the return value is a list with all tax calculations")
def step_impl(context):
    if not isinstance(context.response, list) or len(context.response) != 3:
        raise Exception("The returned response must be a list with all tax calculations")

    if context.response[0] != "1" or context.response[1] != "2" or context.response[2] != "3":
        raise Exception("The returned response must have all previous tax calculations")


@then("the return value is an empty list")
def step_impl(context):
    expect(context.response).be.eq([])


def _tax_calculator_side_effect_1(sale_item, previous_taxes):
    global tax_calculator_1_previous_taxes
    tax_calculator_1_previous_taxes = []
    for tax in previous_taxes:
        tax_calculator_1_previous_taxes.append(tax)
    all_responses.append(1)
    return "1"


def _tax_calculator_side_effect_2(sale_item, previous_taxes):
    global tax_calculator_2_previous_taxes
    tax_calculator_2_previous_taxes = []
    for tax in previous_taxes:
        tax_calculator_2_previous_taxes.append(tax)
    all_responses.append(2)
    return "2"


def _tax_calculator_side_effect_3(sale_item, previous_taxes):
    global tax_calculator_3_previous_taxes
    tax_calculator_3_previous_taxes = []
    for tax in previous_taxes:
        tax_calculator_3_previous_taxes.append(tax)
    all_responses.append(3)
    return "3"
