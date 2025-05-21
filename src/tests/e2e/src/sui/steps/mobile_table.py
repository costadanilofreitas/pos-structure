# encoding=utf8
from behave import *
from helper.selenium_helper import click_the_button, find_elements, send_keys_to_input
from selenium.webdriver.common.by import By
from common import driver_options


@step("mobile POS {pos_function} opens table {table_num}")
def step_impl(context, pos_function, table_num):
    driver = driver_options(context, pos_function)

    send_keys_to_input(driver, table_num, path="test_NumPad_INPUT")
    click_the_button(driver, path="test_TableList_OPEN-TABLE")


@step("mobile POS {pos_function} checks if {product_name} is ordered")
def step_impl(context, pos_function, product_name):
    driver = driver_options(context, pos_function)

    product_path = "//div[contains(@class, 'sale-panel-item-desc')]"
    elements = find_elements(driver, product_path, find_type=By.XPATH, mandatory=True)
    if product_name != elements[0].text:
        raise Exception('Cannot find the order')


@step("mobile POS {pos_function} checks if table's {info} is {result_info}")
def step_impl(context, pos_function, info, result_info):
    driver = driver_options(context, pos_function)

    result_elements = find_elements(driver, 'test_TableDetailsRenderer_INFORIGHT', mandatory=True)
    if info == 'Status':
        if result_info != result_elements[0].text:
            raise Exception('Information does not match')

    if info == 'Setor':
        if result_info != result_elements[1].text:
            raise Exception('Information does not match')

    if info == 'Operador':
        if result_info != result_elements[2].text:
            raise Exception('Information does not match')

    if info == 'Nº de pedidos':
        if result_info != result_elements[3].text:
            raise Exception('Information does not match')

    if info == 'Subtotal':
        if result_info != result_elements[4].text:
            raise Exception('Information does not match')

    if info == 'Assentos':
        if result_info != result_elements[5].text:
            raise Exception('Information does not match')

    if info == 'TM':
        if result_info != result_elements[6].text:
            raise Exception('Information does not match')
