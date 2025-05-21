from behave import *
from helper.selenium_helper import click_the_button, find_elements
from selenium.webdriver.common.by import By
from common import driver_options
import xml.etree.ElementTree as eTree
import os


@step("Totem adds {product_name} to order")
def step_impl(context, product_name):
    driver = driver_options(context, 'totem')

    product_path = "//div[text()='{}']".format(product_name)
    click_the_button(driver, product_path, find_type=By.XPATH)


@step("Totem checks confirmation screen timeout")
def step_impl(context):
    driver = driver_options(context, 'totem')
    confirmation_screen_element = find_elements(driver, 'test_ConfirmationScreenRenderer_SCREEN')

    if not confirmation_screen_element:
        raise Exception("It's not in Confirmation Screen")

    pyscripts_loader = eTree.parse(os.environ["PYLOADER"])
    root = pyscripts_loader.getroot()

    confirmation_screen = list(root.find(".//*[@name='ConfirmationScreen']"))
    threshold = confirmation_screen[0]._children[0].text

    timeout_pyscripts = find_elements(driver, "test_WelcomeScreen_CONTAINER", mandatory=True, timeout=int(threshold)+5)

    if not timeout_pyscripts:
        raise Exception("Screen didn't change!")


@step("Totem checks if it is at welcome screen")
def step_impl(context):
    driver = driver_options(context, 'totem')
    welcome_screen = find_elements(driver, "test_WelcomeScreen_CONTAINER", mandatory=False)

    if welcome_screen:
        click_the_button(driver, "test_WelcomeScreen_CONTAINER")
        click_the_button(driver, "test_saleTypeScreen_EAT-IN")