# encoding=utf8
import sys
import time

from behave import *
from helper.selenium_helper import click_the_button, find_elements
from selenium.webdriver.common.by import By
from common import driver_options

reload(sys)
sys.setdefaultencoding('utf8')


@step("POS {pos_function} selects first table")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)

    table_path = "//button[contains(@class, 'TableItem')][1]"
    click_the_button(driver, table_path, find_type=By.XPATH)


@step("POS {pos_function} selects tab {tab_number}")
def step_impl(context, pos_function, tab_number):
    driver = driver_options(context, pos_function)

    elements = find_elements(driver, "test_TableItem_TAB", mandatory=True, timeout=1.5)
    for tab in elements:
        if tab.text == tab_number:
            click_the_button(driver, element=tab)
            break


@step("POS {pos_function} checks if it's in {view_mode} view")
def step_impl(context, pos_function, view_mode):
    driver = driver_options(context, pos_function)

    element = ''

    if view_mode == 'table':
        element = find_elements(driver, "test_TableList_FA-TH", mandatory=False)
    elif view_mode == 'map':
        element = find_elements(driver, "test_TableList_FA-MAP", mandatory=False)

    if element:
        click_the_button(driver, element=element[0])


@step("POS {pos_function} selects the product {product} from seats")
def step_impl(context, pos_function, product):
    driver = driver_options(context, pos_function)

    time.sleep(1)

    product_path = "//span[contains(text(), '{}')]".format(product)
    click_the_button(driver, product_path, find_type=By.XPATH)


@step("POS {pos_function} selects the seat {seat_num} from rearrange seats")
def step_impl(context, pos_function, seat_num):
    driver = driver_options(context, pos_function)

    seats_path = "//div[contains(@class, 'scrollPanelItemsButtonsHidden')]"
    seats_elements = find_elements(driver, seats_path, find_type=By.XPATH, mandatory=True)

    if seats_elements[int(seat_num)]:
        click_the_button(driver, element=seats_elements[int(seat_num)])
    else:
        raise Exception("Seat not found!")


@step("POS {pos_function} selects {parts_num} parts of the {product}")
def step_impl(context, pos_function, parts_num, product):
    driver = driver_options(context, pos_function)

    elements_path = "//span[contains(text(), '{}')]".format(product)

    for index in range(int(parts_num)):
        products_elements = find_elements(driver, elements_path, find_type=By.XPATH, mandatory=True)
        click_the_button(driver, element=products_elements[index])
