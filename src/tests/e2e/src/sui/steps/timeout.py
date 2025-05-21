import os

from behave import *
from helper.selenium_helper import find_elements
from common import driver_options
import xml.etree.ElementTree as eTree


@step("POS {pos_function} checks timeout popup")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)

    if pos_function.lower() == 'totem':
        pos_number = "12"

    else:
        pos_number = "01"

    posctrl_loader = eTree.parse(os.path.join(os.environ["POSCTRL"], "loader_{}.cfg".format(pos_number)))
    root = posctrl_loader.getroot()

    timeout_seconds = list(root.find(".//*[@name='ScreenTimeout']"))[0].text

    timeout_popup = find_elements(driver, "test_TimeoutDialog_TIMEOUT", mandatory=True, timeout=int(timeout_seconds)+5)

    if not timeout_popup:
        raise Exception("Timeout popup didn't appear!")


@step("Totem checks sale type timeout")
def step_impl(context):
    driver = driver_options(context, 'totem')

    posctrl_loader = eTree.parse(os.path.join(os.environ["POSCTRL"], "loader_12.cfg"))
    root = posctrl_loader.getroot()

    timeout_seconds = list(root.find(".//*[@name='ScreenTimeout']"))[0].text

    timeout_popup = find_elements(driver, "test_WelcomeScreen_CONTAINER", mandatory=True, timeout=int(timeout_seconds)+5)

    if not timeout_popup:
        raise Exception("SaleType didn't exit!")


