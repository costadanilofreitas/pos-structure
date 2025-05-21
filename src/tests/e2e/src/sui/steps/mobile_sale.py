# encoding=utf8
import time

from behave import *
from helper.selenium_helper import click_the_button, find_elements, send_keys_to_input
from selenium.webdriver.common.by import By
from common import driver_options, check_keyboard_input
from sale import check_value


@step("mobile POS {pos_function} selects food category {category} as {food_type}")
def step_impl(context, pos_function, category, food_type):
    driver = driver_options(context, pos_function)

    category_path = "//button[contains(@class, 'button')][text()='{}']".format(category)
    click_the_button(driver, category_path, find_type=By.XPATH)

    type_path = "//button[contains(@class, 'button')][text()='{}']".format(food_type)
    click_the_button(driver, type_path, find_type=By.XPATH)


@step("mobile POS {pos_function} sets quantity to {qty}")
def step_impl(context, pos_function, qty):
    driver = driver_options(context, pos_function)

    click_the_button(driver, path="test_MobileQtyButtonsRenderer_QTY")
    send_keys_to_input(driver, qty, path="test_NumPad_INPUT")
    click_the_button(driver, path="test_NumPadDialog_OK")


@step("mobile POS {pos_function} change price to {price}")
def step_impl(context, pos_function, price):
    driver = driver_options(context, pos_function)

    send_keys_to_input(driver, price, path="test_NumPad_INPUT")
    click_the_button(driver, path="test_NumPadDialog_OK")


@step("mobile POS {pos_function} adds {product_name} to order")
def step_impl(context, pos_function, product_name):
    driver = driver_options(context, pos_function)

    product_path = "//div[text()='{}']".format(product_name)
    click_the_button(driver, product_path, find_type=By.XPATH)


@step("mobile POS {pos_function} checks if order's {row} is {value}")
def step_impl(context, pos_function, row, value):
    driver = driver_options(context, pos_function)
    mobile_check_value(driver, row, value)


@step("mobile POS {pos_function} saves products in every sale type available")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)

    saletype_path = "//button[contains(@class, 'test_SaleType')]"
    saletype_elements = find_elements(driver, saletype_path, find_type=By.XPATH, mandatory=True)
    saletype_list = []
    saletype_class = ''
    recall_screen = ''

    time.sleep(0.5)

    for saletype in saletype_elements:
        saletype_list.append(saletype.text)

    for saletype in saletype_list:
        click_the_button(driver, "test_Header_ORDER")

        if saletype == 'Delivery':
            saletype_class = "test_SaleType_DELIVERY"
            recall_screen = "test_RecallScreen_STORE"

        if saletype == 'Drive':
            saletype_class = "test_SaleType_DRIVE-THRU"
            recall_screen = "test_RecallScreen_DRIVE-THRU"

        if saletype == 'Viagem':
            saletype_class = "test_SaleType_TAKE-OUT"
            recall_screen = "test_RecallScreen_STORE"

        if saletype == 'Loja':
            saletype_class = "test_SaleType_EAT-IN"
            recall_screen = "test_RecallScreen_STORE"

        click_the_button(driver, saletype_class)

        if saletype != 'Delivery':
            click_the_button(driver, "//*[text()='BEBIDAS']", find_type=By.XPATH)
            click_the_button(driver, "//*[text()='CERVEJAS']", find_type=By.XPATH)
            click_the_button(driver, "//*[text()='BUDWEISER']", find_type=By.XPATH)
        else:
            click_the_button(driver, "//*[text()='APPLEBEES']", find_type=By.XPATH)
            click_the_button(driver, "//*[text()='PROMOÇÔES']", find_type=By.XPATH)
            click_the_button(driver, "//*[text()='RIBS 1 PESSOA DL']", find_type=By.XPATH)

        click_the_button(driver, "test_OrderFunctions_SAVEORDER")
        check_keyboard_input(driver)

        click_the_button(driver, "test_Header_RECALL")
        click_the_button(driver, recall_screen)
        click_the_button(driver, "test_RecallScreen_PREVIEW")

        if saletype != 'Delivery':
            check_value(driver, "SUBTOTAL", "11,90")
            check_value(driver, "TOTAL", "11,90")
            check_value(driver, "PAID", "0,00")
            check_value(driver, "CHANGE", "0,00")
        else:
            check_value(driver, "SUBTOTAL", "45,90")
            check_value(driver, "TOTAL", "45,90")
            check_value(driver, "PAID", "0,00")
            check_value(driver, "CHANGE", "0,00")

        click_the_button(driver, "test_OrderPreviewDialog_CLOSE")
        click_the_button(driver, "test_RecallScreen_CANCEL")
        click_the_button(driver, "test_MessageOptionsDialog_OK")


def mobile_check_value(driver, row, value):
    element = find_elements(driver, "test_OrderTotalRenderer_" + row, mandatory=True)

    total_price = element[0].text

    if total_price != "R$ " + value:
        raise Exception("Values didn't match!")