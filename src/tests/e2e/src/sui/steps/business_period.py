from behave import *
from helper.selenium_helper import click_the_button, send_keys_to_input
from selenium.webdriver.common.by import By


@step("user navigates to manager menu")
def step_impl(context):
    click_the_button(context.pos_driver, "test_Header_MANAGER-MENU")
    send_keys_to_input(context.pos_driver, "1000", ".test_NumPadDialog_CONTAINER .numpad-input", By.CSS_SELECTOR)
    click_the_button(context.pos_driver, "test_NumPadDialog_OK")
    send_keys_to_input(context.pos_driver, "1000", ".test_NumPadDialog_CONTAINER .numpad-input", By.CSS_SELECTOR)
    click_the_button(context.pos_driver, "test_NumPadDialog_OK")
