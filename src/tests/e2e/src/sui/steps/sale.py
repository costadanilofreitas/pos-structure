# encoding=utf8
import os
import sys
import math
import time
import xml.etree.ElementTree as eTree

from behave import *
from common import driver_options, check_keyboard_input
from helper.selenium_helper import click_the_button, find_elements, send_keys_to_input
from selenium.webdriver.common.by import By

reload(sys)
sys.setdefaultencoding('utf8')


@step("POS {pos_function} sets quantity to {qty}")
def step_impl(context, pos_function, qty):
    driver = driver_options(context, pos_function)

    if int(qty) <= 10 and qty != '0':
        click_the_button(driver, path="test_QtyButtonsRenderer_{}".format(qty))
    else:
        click_the_button(driver, path="test_QtyButtonsRenderer_SELECTOR")
        send_keys_to_input(driver, qty, path="test_NumPad_INPUT")
        click_the_button(driver, path="test_NumPadDialog_OK")


@step("POS {pos_function} adds {product_name} to order")
def step_impl(context, pos_function, product_name):
    driver = driver_options(context, pos_function)

    product_path = "//*[text()='{}']".format(product_name)
    click_the_button(driver, product_path, find_type=By.XPATH)


@step("POS {pos_function} selects {option} from the order's modifiers")
def step_impl(context, pos_function, option):
    driver = driver_options(context, pos_function)

    option_path = "//div[text()='{}']".format(option)
    click_the_button(driver, option_path, find_type=By.XPATH)



@step("POS {pos_function} pays {value} reais in cash")
def step_impl(context, pos_function, value):
    driver = driver_options(context, pos_function)

    click_the_button(driver, path="test_NumPad_CLEAR")
    send_keys_to_input(driver, value + "00", path="test_NumPad_INPUT")
    click_the_button(driver, path="test_OrderTender_CASH")
    click_the_button(driver, path="test_MessageOptionsDialog_OK")


@step("POS {pos_function} adds {product_name} and pay")
def step_imp(context, pos_function, product_name):
    driver = driver_options(context, pos_function)
    product_path = "//div[text()='{}']".format(product_name)
    click_the_button(driver, product_path, find_type=By.XPATH)
    click_the_button(driver, "test_OrderFunctions_TOTAL-ORDER")

    input_element = find_elements(driver, "test_NumPadDialog_OK", mandatory=False, timeout=1.5)

    if input_element:
        click_the_button(driver, "test_NumPadDialog_OK")

    click_the_button(driver, "test_OrderTender_CASH")
    click_the_button(driver, "test_MessageOptionsDialog_OK")


@step("POS {pos_function} adds products until skim level 3")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)

    storecfg_loader = eTree.parse(os.environ["STORECFGLOADER"])
    root = storecfg_loader.getroot()
    sangria_level_3 = list(root.find(".//*[@name='SangriaLevels']").iter('string'))[0].text.split(";")[2]
    whisky_number = math.ceil(int(sangria_level_3) / 31.90)
    whisky_path = "//*[text()='WHISKY 12 ANOS']"
    for _ in range(int(math.ceil(whisky_number/10))):
        click_the_button(driver, path="test_QtyButtonsRenderer_10")
        time.sleep(1)
        click_the_button(driver, whisky_path, find_type=By.XPATH)
        time.sleep(1)


@step("POS {pos_function} saves products in every sale type available")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)

    saletype_path = "//button[contains(@class, 'test_SaleType')]"
    saletype_elements = find_elements(driver, saletype_path, find_type=By.XPATH, mandatory=True)

    saletype_list = []
    saletype_class = ''
    recall_class = ''
    subtotal_value = ''
    total_value = ''
    change_value = ''
    paid_value = ''
    product = ''

    for saletype in saletype_elements:
        saletype_list.append(saletype.text)

    for saletype in saletype_list:
        click_the_button(driver, "test_Header_ORDER")

        if saletype == 'Delivery':
            saletype_class = "test_SaleType_DELIVERY"
            product = "COWBOY BURGUER DL"
            total_value = "48,90"
            subtotal_value = "48,90"
            paid_value = "0,00"
            change_value = "0,00"

        if saletype == 'Drive':
            saletype_class = "test_SaleType_DRIVE-THRU"
            recall_class = "test_RecallScreen_DRIVE-THRU"

        if saletype == 'Viagem':
            saletype_class = "test_SaleType_TAKE-OUT"

        if saletype == 'Loja':
            saletype_class = "test_SaleType_EAT-IN"

        if saletype != 'Delivery':
            product = "BUDWEISER"
            subtotal_value = "11,90"
            total_value = "11,90"
            paid_value = "0,00"
            change_value = "0,00"

        if saletype != 'Drive':
            recall_class = "test_RecallScreen_STORE"

        click_the_button(driver, saletype_class)
        click_the_button(driver, "//div[text()='{}']".format(product), find_type=By.XPATH)
        click_the_button(driver, "test_OrderFunctions_STORE-ORDER")

        check_keyboard_input(driver)

        click_the_button(driver, "test_Header_RECALL")

        time.sleep(0.2)

        click_the_button(driver, recall_class)
        click_the_button(driver, "test_RecallScreen_PREVIEW")

        check_value(driver, "SUBTOTAL", subtotal_value)
        check_value(driver, "TOTAL", total_value)
        check_value(driver, "PAID", paid_value)
        check_value(driver, "CHANGE", change_value)

        click_the_button(driver, "test_OrderPreviewDialog_CLOSE")
        click_the_button(driver, "test_RecallScreen_CANCEL")
        click_the_button(driver, "test_MessageOptionsDialog_OK")


def check_value(driver, row, value):
    element = find_elements(driver, "test_SaleSummaryLine_" + row, mandatory=True)

    total_price = element[0].text

    if total_price != value:
        raise Exception("Values didn't match!")
