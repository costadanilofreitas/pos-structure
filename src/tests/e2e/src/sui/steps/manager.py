# encoding=utf8
from behave import *
from helper.selenium_helper import click_the_button, find_elements
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from common import driver_options


@step("POS {pos_function} checks if there is closed order to cancel then cancel it")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)

    cancel_order = find_elements(driver, "test_OrderPreviewDialog_OK", mandatory=False, timeout=1.5)

    if cancel_order:
        click_the_button(driver, "test_OrderPreviewDialog_OK")
        click_the_button(driver, "test_MessageOptionsDialog_OK")
    else:
        click_the_button(driver, "test_MessageOptionsDialog_OK")


@step("POS {pos_function} checks if there is {report}")
def step_impl(context, pos_function, report):
    driver = driver_options(context, pos_function)

    header_element = find_elements(driver, "test_Header_MANAGER-MENU", mandatory=False, timeout=1.5)

    if report == 'logoff report':
        if 'posid=1' in header_element[0].parent.current_url:
            click_the_button(driver, "test_ManagerScreen_LOGOFF-REPORT")
            click_the_button(driver, "test_NumPadDialog_OK")
            close_element = find_elements(driver, "test_TextPreviewDialog_CLOSE")

            if close_element:
                click_the_button(driver, "test_TextPreviewDialog_CLOSE")

            else:
                click_the_button(driver, "test_MessageOptionsDialog_OK")

    if report == 'session id':
        if 'posid=1' in header_element[0].parent.current_url:
            click_the_button(driver, "test_ManagerScreen_SESSION-ID-REPORT")
            click_the_button(driver, "test_MessageOptionsDialog_CLOSE")


@step("POS {pos_function} checks if last report value was {value}")
def step_impl(context, pos_function, value):
    driver = driver_options(context, pos_function)

    scroll_panel(driver)

    date_element = find_elements(driver, "test_ScrollPanelListItems_DATE", mandatory=True)
    click_the_button(driver, element=date_element[-1])

    report_path = "//pre"
    report_element = find_elements(driver, report_path, find_type=By.XPATH, mandatory=True)
    report_content = report_element[0].text.replace("\n", "").replace(" ", "").replace(".", "").replace("=", "")\
        .replace(",", "")

    if "Valor:R$" + value.replace(",", "") not in report_content:
        raise Exception("Value didn't match!")


def scroll_panel(driver):
    scroll = True
    scroll_path = "//button[contains(@class, 'scroll-panel-button-down')]"
    while scroll:
        scroll_element = find_elements(driver, scroll_path, find_type=By.XPATH)
        if scroll_element:
            if 'disabled' in scroll_element[0].get_attribute("class"):
                scroll = False

            else:
                try:
                    click_the_button(driver, element=scroll_element[0])
                except StaleElementReferenceException:
                    return 'ScrollDown button not found!'

        else:
            scroll = False
