from behave import *
from helper.selenium_helper import find_elements
from selenium.webdriver.common.by import By
from common import driver_options


@step("POS {pos_function} the system store the sales report data")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)
    report_lines = find_elements(driver, "//p[contains(@class, 'PrintPreviewDialog')]", find_type=By.XPATH)
    for line in report_lines:
        if "Venda Bruta" in line.text:
            context.gross_sales_value = _get_line_value(line.text)
            context.gross_sales_quantity = _get_line_quantity(line.text)
        elif "Descontos" in line.text:
            context.discounts_value = _get_line_value(line.text)
            context.discounts_quantity = _get_line_quantity(line.text)
        elif "Venda Aberta" in line.text:
            context.billed_sales_value = _get_line_value(line.text)
            context.billed_sales_quantity = _get_line_quantity(line.text)
        elif "Venda Faturada" in line.text:
            context.opened_sales_value = _get_line_value(line.text)
            context.opened_sales_quantity = _get_line_quantity(line.text)
        elif "Gorjetas" in line.text:
            context.tips_value = _get_line_value(line.text)
            context.tips_quantity = _get_line_quantity(line.text)


def _get_line_value(text):
    return float(text.split("R$")[-1].strip().replace(",", "."))


def _get_line_quantity(text):
    return int(text.split("[")[-1].split("]")[0].strip())
