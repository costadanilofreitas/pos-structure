# coding=utf-8
import os
import xml.etree.ElementTree as eTree

from behave import *
from common import driver_options
from helper.selenium_helper import find_elements
from selenium.webdriver.common.by import By


@step("POS {pos_function} checks if item {item} is in rupture")
def step_impl(context, pos_function, item):
    driver = driver_options(context, pos_function)
    disabled_items = find_elements(driver, "test_RuptureDialog_DISABLED-ITEMS")

    if item not in disabled_items[0].text:
        raise Exception("Values didn't match!")


@step("POS {pos_function} checks if item {item} is not in rupture")
def step_impl(context, pos_function, item):
    driver = driver_options(context, pos_function)
    enabled_items = find_elements(driver, "test_RuptureDialog_ENABLED-ITEMS")

    if item not in enabled_items[0].text:
        raise Exception("Values didn't match!")


@step("POS {pos_function} checks if item {item} is in rupture exit")
def step_impl(context, pos_function, item):
    driver = driver_options(context, pos_function)
    enabled_items = find_elements(driver, "test_RuptureConfirmation_EXIT-ITEMS")

    if item not in enabled_items[0].text:
        raise Exception("Values didn't match!")


@step("POS {pos_function} checks if item {item} is in rupture enter")
def step_impl(context, pos_function, item):
    driver = driver_options(context, pos_function)
    enabled_items = find_elements(driver, "test_RuptureConfirmation_ENTER-ITEMS")

    if item not in enabled_items[0].text:
        raise Exception("Values didn't match!")


@step("POS {pos_function} checks if product {product} is ruptured")
def step_impl(context, pos_function, product):
    driver = driver_options(context, pos_function)

    if pos_function == 'totem':
        loader = "loader_12.cfg"
    else:
        loader = "loader_01.cfg"

    posctrl_loader = eTree.parse(os.path.join(os.environ["POSCTRL"], "{}".format(loader)))
    root = posctrl_loader.getroot()
    show_ruptured_products = list(root.find(".//*[@name='ShowRupturedProducts']"))[0].text

    if show_ruptured_products.lower() == 'true':
        element_path = "//*[text()='Indisponível']"
        element_result = find_elements(driver, element_path, find_type=By.XPATH, mandatory=True)

        if not element_result:
            raise Exception("Element 'indisponivel' not found!")

    else:
        element_path = "//*[text()='{}']".format(product)
        element_result = find_elements(driver, element_path, find_type=By.XPATH, mandatory=True)

        if element_result:
            raise Exception("Element {} still on screen!".format(product))


@step("POS {pos_function} checks if product {product} is not ruptured")
def step_impl(context, pos_function, product):
    driver = driver_options(context, pos_function)
    unavailable_path = "//*[text()='Indisponível']"
    unavailable_result = find_elements(driver, unavailable_path, find_type=By.XPATH, mandatory=True)
    product_path = "//*[text()='{}']".format(product)
    product_result = find_elements(driver, product_path, find_type=By.XPATH, mandatory=True)

    if not product_result and unavailable_result:
        raise Exception("Product {} still in rupture!".format(product))
