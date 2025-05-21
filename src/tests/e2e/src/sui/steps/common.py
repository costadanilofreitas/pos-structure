import time
import os

from behave import *
from helper.selenium_helper import click_the_button, double_click_the_button, send_keys_to_input, find_elements
from sui.environment import get_chrome_driver_webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException
import xml.etree.ElementTree as eTree


@step("user clicks on the {button_path}")
def step_impl(context, button_path):
    click_the_button(context.pos_driver, button_path)


@step("user double clicks on the {button_path}")
def step_impl(context, button_path):
    double_click_the_button(context.pos_driver, button_path)


@step("POS {pos_function} checks if there's option dialog to close")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)

    dialog_element = find_elements(driver, "test_MessageOptionsDialog_CLOSE", mandatory=False)

    if dialog_element:
        click_the_button(driver, "test_MessageOptionsDialog_CLOSE")


@step("POS {pos_function} checks if there's option dialog to click ok")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)

    dialog_element = find_elements(driver, "test_MessageOptionsDialog_OK", mandatory=False)

    if dialog_element:
        click_the_button(driver, "test_MessageOptionsDialog_OK")


@step("POS {pos_function} checks if needs to print")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)

    dialog_element = find_elements(driver, "test_MessageOptionsDialog_PRINT", mandatory=False)

    if dialog_element:
        click_the_button(driver, "test_MessageOptionsDialog_PRINT")


@step("POS {pos_function} delete text")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)
    keyboard_element = find_elements(driver, "test_KeyboardInput_INPUT", mandatory=False)
    text = keyboard_element[0].get_attribute("value")

    for _ in text:
        click_the_button(driver, "test_KeyboardInput_DELETE")


@step("POS {pos_function} clicks on the {button_path}")
def step_impl(context, pos_function, button_path):
    driver = driver_options(context, pos_function)

    try:
        click_the_button(driver, button_path)

    except ElementClickInterceptedException:
        time.sleep(3)
        click_the_button(driver, button_path)


@step("user opens POS {pos_function} in {mode}")
def step_impl(context, pos_function, mode):
    if pos_function.lower() == 'qsr-fl-fl':
        context.pos_qsr_fl_fl = get_chrome_driver_webdriver(1, context, mode)

    elif pos_function.lower() == 'qsr-fc-ot':
        context.pos_qsr_fc_ot = get_chrome_driver_webdriver(2, context, mode)

    elif pos_function.lower() == 'qsr-fc-cs':
        context.pos_qsr_fc_cs = get_chrome_driver_webdriver(3, context, mode)

    elif pos_function.lower() == 'ts-fl-fl':
        context.pos_ts_fl_fl = get_chrome_driver_webdriver(4, context, mode)

    elif pos_function.lower() == 'ts-ts-fl':
        context.pos_ts_ts_fl = get_chrome_driver_webdriver(5, context, mode)

    elif pos_function.lower() == 'ts-fl-cs':
        context.pos_ts_fl_cs = get_chrome_driver_webdriver(6, context, mode)

    elif pos_function.lower() == 'totem':
        context.totem = get_chrome_driver_webdriver(12, context, mode)

    else:
        raise Exception("POS not defined!")


@step("user opens EXPO")
def step_impl(context):
    context.expo = get_chrome_driver_webdriver(1, context, "kui")


@step("user opens PICKUP")
def step_impl(context):
    context.pickup = get_chrome_driver_webdriver(5, context, "kui")


@step("user opens PREP {prep_screen}")
def step_impl(context, prep_screen):
    if prep_screen.lower() == 'prep-frito':
        context.prep_frito = get_chrome_driver_webdriver(2, context, "kui")

    elif prep_screen.lower() == 'prep-chapa':
        context.prep_chapa = get_chrome_driver_webdriver(3, context, "kui")

    elif prep_screen.lower() == 'prep-grelha':
        context.prep_grelha = get_chrome_driver_webdriver(4, context, "kui")

    else:
        raise Exception("PREP not defined!")


@step("POS {pos_function} authenticate as manager")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)

    input_element = find_elements(driver, "test_NumPad_INPUT", mandatory=False, timeout=1.5)

    if input_element:
        send_keys_to_input(driver, "1000", path="test_NumPad_INPUT")
        click_the_button(driver, "test_NumPadDialog_OK")
        send_keys_to_input(driver, "1000", path="test_NumPad_INPUT")
        click_the_button(driver, "test_NumPadDialog_OK")

        message_element = find_elements(driver, "test_MessageOptionsDialog_OK", mandatory=False,
                                        timeout=1.5)

        if message_element:
            click_the_button(driver, "test_MessageOptionsDialog_OK")
            click_the_button(driver, "test_MessageOptionsDialog_CLOSE")


@step("POS {pos_function} sets value to {value}")
def step_impl(context, pos_function, value):
    driver = driver_options(context, pos_function)

    send_keys_to_input(driver, value + '00', ".test_NumPadDialog_CONTAINER .numpad-input",
                       By.CSS_SELECTOR)
    click_the_button(driver, "test_NumPadDialog_OK")


@step("POS {pos_function} checks if dialog text is {text}")
def step_impl(context, pos_function, text):
    driver = driver_options(context, pos_function)

    text_element = find_elements(driver, path="test_MessageOptionsDialog_MESSAGE")

    if text_element[0].text != text:
        raise Exception("Dialog text didn't match!")


@step("POS {pos_function} checks if needs to change to {tab} tab")
def step_impl(context, pos_function, tab):
    driver = driver_options(context, pos_function)

    selection_path = "//button[contains(@class, 'pressedButton')]"
    selection_element = find_elements(driver, selection_path, find_type=By.XPATH, mandatory=True)
    tab_name = "test_Header_{}".format(tab.upper())
    if selection_element:
        if tab_name not in selection_element[0].get_attribute("class"):
            click_the_button(driver, path=tab_name)

    else:
        click_the_button(driver, path=tab_name)


@step("POS {pos_function} send input {input_value} to {input_type}")
def step_impl(context, pos_function, input_value, input_type):
    driver = driver_options(context, pos_function)

    if input_type.lower() == 'numpad':
        send_keys_to_input(driver, input_value, path="test_NumPad_INPUT")
    elif input_type.lower() == 'keyboard':
        send_keys_to_input(driver, input_value, path="test_KeyboardInput_INPUT")


@step("POS {pos_function} checks if order's {row} is equal to {value}")
def step_impl(context, pos_function, row, value):
    driver = driver_options(context, pos_function)

    check_value(driver, row, value)


@step("user closes POS {pos_function}")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)

    driver.quit()


@step("POS {pos_function} selects the filter {filter_value}")
def step_impl(context, pos_function, filter_value):
    driver = driver_options(context, pos_function)

    filter_path = "//p[text()='{}']".format(filter_value)
    click_the_button(driver, filter_path, find_type=By.XPATH)


@step("POS {pos_function} checks if icon {icon} is on screen")
def step_impl(context, pos_function, icon):
    driver = driver_options(context, pos_function)

    element_path = "//i[contains(@class, '{}')]".format(icon)
    element_result = find_elements(driver, element_path, find_type=By.XPATH, mandatory=True)

    if not element_result:
        raise Exception("Icon {} not found!".format(icon))


@step("POS {pos_function} checks if icon {icon} isn't on screen")
def step_impl(context, pos_function, icon):
    driver = driver_options(context, pos_function)

    element_path = "//i[contains(@class, '{}')]".format(icon)
    element_result = find_elements(driver, element_path, find_type=By.XPATH, mandatory=True)

    if element_result:
        raise Exception("Icon {} still on screen!".format(icon))


@step("POS {pos_function} checks if there's element {element} on screen")
def step_impl(context, pos_function, element):
    driver = driver_options(context, pos_function)

    element_path = "//*[text()='{}']".format(element)
    element_result = find_elements(driver, element_path, find_type=By.XPATH, mandatory=True)

    if not element_result:
        raise Exception("Element {} not found!".format(element))


@step("POS {pos_function} checks if there isn't element {element} on screen")
def step_impl(context, pos_function, element):
    driver = driver_options(context, pos_function)

    element_path = "//*[text()='{}']".format(element)
    element_result = find_elements(driver, element_path, find_type=By.XPATH, mandatory=True)

    if element_result:
        raise Exception("Element {} on screen!".format(element))


@step("POS {pos_function} clicks the element with text {element}")
def step_impl(context, pos_function, element):
    driver = driver_options(context, pos_function)

    element_path = "//*[text()='{}']".format(element)
    click_the_button(driver, element_path, find_type=By.XPATH)


@step("POS {pos_function} tests all payment options")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)

    paytype_path = "//button[contains(@class, 'test_OrderTender_')]"
    paytype_elements = find_elements(driver, paytype_path, find_type=By.XPATH, mandatory=True)

    for paytype in paytype_elements:
        if paytype.text != 'Limpar Desconto' and paytype.text != 'Aplicar Desconto':
            if paytype.text != 'Outros':
                click_the_button(driver, path="test_NumPad_CLEAR")
                send_keys_to_input(driver, "1", path="test_NumPad_INPUT")
                click_the_button(driver, element=paytype)

                filter_list = check_filters(driver)

                if filter_list:
                    click_the_button(driver, path="test_FilterableList_CANCEL")
                    for element in filter_list:
                        click_the_button(driver, path="test_NumPad_CLEAR")
                        send_keys_to_input(driver, "1", path="test_NumPad_INPUT")
                        click_the_button(driver, element=paytype)

                        filter_path = "//p[contains(@class, 'Filter')][text()='{}']".format(element)

                        click_the_button(driver, filter_path, find_type=By.XPATH)
                        click_the_button(driver, path="test_FilterableList_OK")
                        click_the_button(driver, path="test_MessageOptionsDialog_OK")
                else:
                    click_the_button(driver, path="test_MessageOptionsDialog_OK")
            else:
                click_the_button(driver, element=paytype)
                other_payments = check_filters(driver)
                click_the_button(driver, path="test_FilterableList_CANCEL")

                for payment in other_payments:
                    click_the_button(driver, path="test_NumPad_CLEAR")
                    send_keys_to_input(driver, "1", path="test_NumPad_INPUT")
                    click_the_button(driver, element=paytype)

                    payment_path = "//p[contains(@class, 'Filter')][text()='{}']".format(payment)
                    click_the_button(driver, payment_path, find_type=By.XPATH)
                    click_the_button(driver, path="test_FilterableList_OK")

                    options_list = check_filters(driver)

                    if options_list:
                        click_the_button(driver, path="test_FilterableList_CANCEL")
                        for option in options_list:
                            click_the_button(driver, path="test_NumPad_CLEAR")
                            send_keys_to_input(driver, "1", path="test_NumPad_INPUT")
                            click_the_button(driver, element=paytype)

                            click_the_button(driver, payment_path, find_type=By.XPATH)
                            click_the_button(driver, path="test_FilterableList_OK")

                            option_path = "//p[contains(@class, 'Filter')][text()='{}']".format(option)
                            click_the_button(driver, option_path, find_type=By.XPATH)
                            click_the_button(driver, path="test_FilterableList_OK")
                            click_the_button(driver, path="test_MessageOptionsDialog_OK")

                    else:
                        click_the_button(driver, path="test_MessageOptionsDialog_OK")
                        if payment == "MERCADO PAGO":
                            yes_element = find_elements(driver, "test_MessageOptionsDialog_YES")
                            if yes_element:
                                click_the_button(driver, "test_MessageOptionsDialog_YES")


@step("POS {pos_function} checks if there's option dialog to click yes")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)
    yes_element = find_elements(driver, 'test_MessageOptionsDialog_YES')
    if yes_element:
        click_the_button(driver, 'test_MessageOptionsDialog_YES')


@step("POS {pos_function} select order {order}")
def step_impl(context, pos_function, order):
    driver = driver_options(context, pos_function)
    order_path = "//div[contains(text(), '{}')]".format(order)
    order_element = find_elements(driver, order_path, find_type=By.XPATH)

    if order_element:
        click_the_button(driver, element=order_element[0])


@step("POS {pos_function} checks if total is {total}")
def step_impl(context, pos_function, total):
    driver = driver_options(context, pos_function)
    total_path = "//div[contains(@class, 'test_OrderTotalRenderer_TOTAL')"
    total_element = find_elements(driver, total_path, find_type=By.XPATH)

    if total_element and total_element[0].text != total:
        raise Exception("Values didn't match!")


@step("POS {pos_function} checks if options is disabled")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)
    options_element = find_elements(driver, "test_OrderFunctions_OPTIONS")
    if options_element:
        raise Exception("Options is enabled!")


@step("POS {pos_function} waits {second} seconds")
def step_impl(context, pos_function, second):
    time.sleep(float(second))


@step("POS {pos_function} checks thresholds")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)

    exception_message = "Threshold didn't match!"

    kds_loader = eTree.parse(os.environ["NKDSLOADER"])
    root = kds_loader.getroot()
    thresholds = []
    if pos_function.lower() == 'prep-frito':
        thresholds = list(root.find(".//*[@name='FRITO_IN_PROGRESS']").find(".//*[@name='Thresholds']").iter('string'))

    if pos_function.lower() == 'expo':
        thresholds = list(root.find(".//*[@name='EXPO']").find(".//*[@name='Thresholds']").iter('string'))

    if len(thresholds) > 0:
        threshold_1 = thresholds[0].text.split('#')[0].split(':')
        threshold_1_seconds = (int(threshold_1[0]) * 3600) + (int(threshold_1[1]) * 60) + (int(threshold_1[2]))

        threshold_2 = thresholds[1].text.split('#')[0].split(':')
        threshold_2_seconds = (int(threshold_2[0]) * 3600) + (int(threshold_2[1]) * 60) + (int(threshold_2[2]))

        threshold_cell = find_elements(driver, "//div[contains(@class, 'threshold_0')]", find_type=By.XPATH)
        if not threshold_cell:
            raise Exception(exception_message)

        time.sleep(threshold_1_seconds)
        click_the_button(driver, "test_FooterRenderer_REFRESH")
        threshold_cell = find_elements(driver, "//div[contains(@class, 'threshold_1')]", find_type=By.XPATH)

        if not threshold_cell:
            raise Exception(exception_message)

        time.sleep((threshold_2_seconds - threshold_1_seconds))
        click_the_button(driver, "test_FooterRenderer_REFRESH")
        threshold_cell = find_elements(driver, "//div[contains(@class, 'threshold_2')]", find_type=By.XPATH)

        if not threshold_cell:
            raise Exception(exception_message)

    else:
        raise Exception("Thresholds not found")


@step("POS {pos_function} enters name {name} if needed")
def step_impl(context, pos_function, name):
    driver = driver_options(context, pos_function)

    input_element = find_elements(driver, "test_KeyboardInput_INPUT", mandatory=False, timeout=1.5)

    if input_element:
        send_keys_to_input(driver, name, path="test_KeyboardInput_INPUT")
        click_the_button(driver, "test_KeyboardDialog_OK")


@step("POS {pos_function} checks if needs to open day")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)
    day_closed_element = find_elements(driver, "//span[contains(text(), 'Fechado')]", find_type=By.XPATH)

    if day_closed_element:
        context.execute_steps(u"""
        Then POS QSR-FL-FL clicks on the test_Header_MANAGER-MENU
        And POS QSR-FL-FL waits 1 seconds
        And POS QSR-FL-FL authenticates the operator 1000 if needed
        And POS QSR-FL-FL checks if needs to close day
        And POS QSR-FL-FL waits 1 seconds
        And POS QSR-FL-FL clicks on the test_ManagerScreen_OPEN-DAY
        And POS QSR-FL-FL waits 1 seconds
        And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
        And POS QSR-FL-FL waits 1 seconds
        And POS QSR-FL-FL checks if needs to print
        """)


@step("POS {pos_function} skip CPF if needed")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)

    input_element = find_elements(driver, "test_NumPadDialog_OK", mandatory=False, timeout=1.5)

    if input_element:
        click_the_button(driver, "test_NumPadDialog_OK")


@step("POS {pos_function} checks scroll {orientation}")
def step_impl(context, pos_function, orientation):
    driver = driver_options(context, pos_function)

    scroll_element = find_elements(driver, "test_ScrollPanel_{}".format(orientation.upper()), mandatory=False,
                                   timeout=1.5)

    if not scroll_element:
        raise Exception('Scroll not found')


def check_value(driver, row, value):
    import time
    time.sleep(1.0)

    element = find_elements(driver, "test_SaleSummaryLine_" + row, mandatory=True)

    total_price = element[0].text

    if total_price != value:
        raise Exception("Values didn't match!")


def driver_options(context, pos_function):
    if pos_function.lower() == 'qsr-fl-fl':
        return context.pos_qsr_fl_fl

    elif pos_function.lower() == 'qsr-fc-ot':
        return context.pos_qsr_fc_ot

    elif pos_function.lower() == 'qsr-fc-cs':
        return context.pos_qsr_fc_cs

    elif pos_function.lower() == 'ts-fl-fl':
        return context.pos_ts_fl_fl

    elif pos_function.lower() == 'ts-ts-fl':
        return context.pos_ts_ts_fl

    elif pos_function.lower() == 'ts-fl-cs':
        return context.pos_ts_fl_cs

    elif pos_function.lower() == 'expo':
        return context.expo

    elif pos_function.lower() == 'prep-frito':
        return context.prep_frito

    elif pos_function.lower() == 'prep-grelha':
        return context.prep_grelha

    elif pos_function.lower() == 'prep-chapa':
        return context.prep_chapa

    elif pos_function.lower() == 'totem':
        return context.totem

    elif pos_function.lower() == 'pickup':
        return context.pickup

    else:
        raise Exception("POS not defined!")


def check_keyboard_input(driver):
    keyboard_element = find_elements(driver, "test_KeyboardInput_INPUT", mandatory=False)

    if keyboard_element:
        send_keys_to_input(driver, "Nome do Cliente", path="test_KeyboardInput_INPUT")
        click_the_button(driver, "test_KeyboardDialog_OK")


def check_filters(driver):
    filter_path = "//p[contains(@class, 'FilterListBoxRenderer')]"
    filter_elements = find_elements(driver, filter_path, find_type=By.XPATH, mandatory=False, timeout=1)
    filter_list = []

    if filter_elements:
        try:
            for element in filter_elements:
                filter_list.append(element.text)

        except StaleElementReferenceException:
            filter_elements = find_elements(driver, filter_path, find_type=By.XPATH, mandatory=False,
                                            timeout=1)
            try:
                for element in filter_elements:
                    filter_list.append(element.text)

            except TypeError:
                return filter_list

    return filter_list
