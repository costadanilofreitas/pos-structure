# encoding=utf8
import time

from behave import *
from helper.selenium_helper import click_the_button, double_click_the_button, send_keys_to_input, find_elements
from selenium.webdriver.common.by import By
from common import driver_options


@step("POS {pos_function} authenticate the operator {operator_login} login")
def step_impl(context, pos_function, operator_login):
    driver = driver_options(context, pos_function)

    send_keys_to_input(driver, operator_login, ".test_NumPadDialog_CONTAINER .numpad-input",
                       By.CSS_SELECTOR)
    click_the_button(driver, "test_NumPadDialog_OK")
    send_keys_to_input(driver, operator_login, ".test_NumPadDialog_CONTAINER .numpad-input",
                       By.CSS_SELECTOR)
    click_the_button(driver, "test_NumPadDialog_OK")
    click_the_button(driver, "test_MessageOptionsDialog_OK")
    click_the_button(driver, "test_MessageOptionsDialog_PRINT")


@step("POS {pos_function} authenticates the operator {operator_login} if needed")
def step_impl(context, pos_function, operator_login):
    driver = driver_options(context, pos_function)

    input_element = find_elements(driver, "test_NumPad_INPUT", mandatory=False, timeout=1.5)

    if input_element:
        time.sleep(1)

        send_keys_to_input(driver, operator_login, path="test_NumPad_INPUT")
        click_the_button(driver, "test_NumPadDialog_OK")

        time.sleep(1)

        send_keys_to_input(driver, operator_login, path="test_NumPad_INPUT")
        click_the_button(driver, "test_NumPadDialog_OK")

        message_element = find_elements(driver, "test_MessageOptionsDialog_OK", mandatory=False)

        if message_element:
            click_the_button(driver, "test_MessageOptionsDialog_OK")

            close_element = find_elements(driver, "test_MessageOptionsDialog_CLOSE", mandatory=False)

            if close_element:
                click_the_button(driver, "test_MessageOptionsDialog_CLOSE")


@step("POS {pos_function} checks if the operator needs to logout")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)

    logout_element = find_elements(driver, "test_LoginNumpad_SIGNOUT", mandatory=False)

    if logout_element:
        click_the_button(driver, "test_LoginNumpad_SIGNOUT")
        time.sleep(1)
        send_keys_to_input(driver, "1000", path="test_NumPad_INPUT")
        click_the_button(driver, "test_NumPadDialog_OK")
        time.sleep(1)
        send_keys_to_input(driver, "1000", path="test_NumPad_INPUT")
        click_the_button(driver, "test_NumPadDialog_OK")
        time.sleep(1)
        double_click_the_button(driver, "test_BordereauDialog_TITLE")
        click_the_button(driver, "test_BordereauDialog_OK")
        time.sleep(1)
        click_the_button(driver, "test_MessageOptionsDialog_CLOSE")

        keyboard_dialog = find_elements(driver, "test_KeyboardDialog_OK", mandatory=True)

        if keyboard_dialog:
            send_keys_to_input(driver, "Quebra de caixa", path="test_KeyboardInput_INPUT")
            click_the_button(driver, "test_KeyboardDialog_OK")
            click_the_button(driver, "test_MessageOptionsDialog_CLOSE")


@step("POS {pos_function} checks if needs to close day")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)

    click_the_button(driver, "test_ManagerScreen_CLOSE-DAY")

    time.sleep(1)

    dialog_element = find_elements(driver, "test_MessageOptionsDialog_YES", mandatory=False)

    if dialog_element:
        click_the_button(driver, "test_MessageOptionsDialog_YES")
    else:
        click_the_button(driver, "test_MessageOptionsDialog_OK")


@step("POS {pos_function} checks if there's bordereau and closes it")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)

    bordereau_element = find_elements(driver, "test_BordereauDialog_TITLE", mandatory=False)

    if bordereau_element:
        double_click_the_button(driver, "test_BordereauDialog_TITLE")
        click_the_button(driver, "test_BordereauDialog_OK")
        click_the_button(driver, "test_MessageOptionsDialog_PRINT")


@step("POS {pos_function} checks if needs to justify")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)

    keyboard_dialog = find_elements(driver, "test_KeyboardDialog_OK", mandatory=False)

    if keyboard_dialog:
        send_keys_to_input(driver, "Quebra de caixa", path="test_KeyboardInput_INPUT")
        click_the_button(driver, "test_KeyboardDialog_OK")
        click_the_button(driver, "test_MessageOptionsDialog_CLOSE")


@step("POS {pos_function} close operator")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)

    dialog_element = find_elements(driver, "test_FilterableList_OK", mandatory=False)

    if dialog_element:
        click_the_button(driver, "test_FilterableList_OK")

        time.sleep(0.8)

        click_the_button(driver, "test_MessageOptionsDialog_OK ")

    else:
        click_the_button(driver, "test_MessageOptionsDialog_OK")

    bordereau_element = find_elements(driver, "test_BordereauDialog_TITLE", mandatory=False)

    if bordereau_element:
        double_click_the_button(driver, "test_BordereauDialog_TITLE")
        click_the_button(driver, "test_BordereauDialog_OK")
        click_the_button(driver, "test_MessageOptionsDialog_PRINT")


@step("POS {pos_function} double clicks bordereau")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)
    double_click_the_button(driver, "test_BordereauDialog_TITLE")