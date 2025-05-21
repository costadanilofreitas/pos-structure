import os
import time

from behave import *
from helper.selenium_helper import click_the_button, find_elements, double_click_the_button
from common import driver_options
from selenium.webdriver.common.by import By
import xml.etree.ElementTree as eTree
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
stored_order_number = None
stored_order_count = None
stored_customer_name = None
stored_footer_counter = None


@step("KDS {pos_function} checks if order {num} is {order}")
def step_impl(context, pos_function, num, order):
    driver = driver_options(context, pos_function)
    order_element = find_elements(driver, "//p[contains(@class, 'LV0')]", find_type=By.XPATH)

    if order != order_element[int(num) - 1].text:
        raise Exception("Values didn't match!")


@step("KDS {pos_function} checks if order is {order}")
def step_impl(context, pos_function, order):
    driver = driver_options(context, pos_function)
    order_element = find_elements(driver, "//p[contains(@class, 'LV0')]", find_type=By.XPATH)

    if order != order_element[0].text:
        raise Exception("Values didn't match!")


@step("KDS {pos_function} checks if food is {food}")
def step_impl(context, pos_function, food):
    driver = driver_options(context, pos_function)
    food_element = find_elements(driver, "//p[contains(@class, 'LV1')]", find_type=By.XPATH)

    if food != food_element[0].text:
        raise Exception("Values didn't match!")


@step("KDS {pos_function} checks if side dish is {side_dish}")
def step_impl(context, pos_function, side_dish):
    driver = driver_options(context, pos_function)
    side_dish_element = find_elements(driver, "//p[contains(@class, 'LV2')]", find_type=By.XPATH)

    if side_dish != side_dish_element[0].text:
        raise Exception("Values didn't match!")


@step("KDS {pos_function} selects cell {cell_number}")
def step_impl(context, pos_function, cell_number):
    driver = driver_options(context, pos_function)

    cell_headers = find_elements(driver, "test_KdsCell_HEADER")

    click_the_button(driver, element=cell_headers[int(cell_number) - 1])


@step("KDS {kds_function} sends bump command {command}")
def step_impl(context, kds_function, command):
    driver = driver_options(context, kds_function)

    # ItemServed
    if command.lower() == 'enter':
        key = Keys.ENTER
    # Undo
    elif command.lower() == 'backspace':
        key = Keys.BACKSPACE
    # Undo
    elif command.lower() == 'numpad_7':
        key = Keys.NUMPAD7
    # NavigateNext
    elif command.lower() == 'numpad_6':
        key = Keys.NUMPAD6
    # NavigateNext
    elif command.lower() == 'right_arrow':
        key = Keys.ARROW_RIGHT
    # NavigatePrevious
    elif command.lower() == 'left_arrow':
        key = Keys.ARROW_LEFT
    # NavigatePrevious
    elif command.lower() == 'numpad_4':
        key = Keys.NUMPAD4
    # NavigateFirst
    elif command.lower() == 'numpad_1':
        key = Keys.NUMPAD1
    # NavigateFirst
    elif command.lower() == '1':
        key = '1'
    # ConsolidatedItems
    elif command.lower() == 'numpad_5':
        key = Keys.NUMPAD5
    # ConsolidatedItems
    elif command.lower() == 'tab':
        key = Keys.TAB
    # ResetCurrentOrder
    elif command.lower() == '-':
        key = '-'
    # ResetCurrentOrder
    elif command.lower() == 'numpad_-':
        key = Keys.SUBTRACT
    # RefreshScreen
    elif command.lower() == 'r':
        key = 'r'
    # RefreshScreen
    elif command.lower() == 'numpad_/':
        key = Keys.DIVIDE
    # ZoomNext
    elif command.lower() == 'z':
        key = 'z'
    # ZoomNext
    elif command.lower() == 'numpad_+':
        key = Keys.ADD

    else:
        raise Exception('Command not defined!')

    actions = ActionChains(driver)
    actions.send_keys(key).perform()


@step("KDS {pos_function} sets zoom to {zoom}")
def step_impl(context, pos_function, zoom):
    driver = driver_options(context, pos_function)

    current_level = get_zoom_level(driver)

    while current_level != zoom:
        click_the_button(driver, "test_FooterRenderer_ZOOM")
        current_level = get_zoom_level(driver)


@step("KDS {pos_function} serves all orders")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)
    serve_element = find_elements(driver, "test_ExpoCell_BODY")
    while serve_element:
        double_click_the_button(driver, "test_ExpoCell_BODY")
        time.sleep(0.5)
        serve_element = find_elements(driver, "test_ExpoCell_BODY")


@step("KDS {pos_function} serves the first order")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)
    double_click_the_button(driver, "test_ExpoCell_BODY")


@step("KDS {pos_function} checks if zoom is {zoom}")
def step_impl(context, pos_function, zoom):
    driver = driver_options(context, pos_function)

    current_level = get_zoom_level(driver)

    if current_level != zoom:
        raise Exception('Current zoom is not at {}'.format(zoom))


@step("KDS {pos_function} checks if page is {page}")
def step_impl(context, pos_function, page):
    driver = driver_options(context, pos_function)

    page_pagination = find_elements(driver, "test_FooterRenderer_PAGINATION", mandatory=True)

    pagination_text = page_pagination[0].text

    if pagination_text.split(':')[-1].replace(' ', '') != page:
        raise Exception('Page is not at {}'.format(page))


@step("KDS {pos_function} checks if saletype is {sale_type}")
def step_impl(context, pos_function, sale_type):
    driver = driver_options(context, pos_function)
    header_type_element = find_elements(driver, "test_KdsCellHeader_HEADER")
    if sale_type not in header_type_element[0].text:
        raise Exception("Values didn't match!")


@step("KDS {pos_function} checks if cell {num} saletype is {sale_type}")
def step_impl(context, pos_function, num, sale_type):
    driver = driver_options(context, pos_function)
    header_type_element = find_elements(driver, "test_KdsCell_HEADER")
    if sale_type.lower() not in header_type_element[int(num) - 1].text.lower():
        raise Exception("Values didn't match!")


@step("KDS {pos_function} checks order {order} on ConsolidatedItemsList")
def step_impl(context, pos_function, order):
    driver = driver_options(context, pos_function)
    list_element = find_elements(driver, "test_ConsolidatedItems_CONTAINER")
    if order not in list_element[0].text.replace("\n", " "):
        raise Exception("Values didn't match!")


@step("KDS {pos_function} serves cell {num}")
def step_impl(context, pos_function, num):
    driver = driver_options(context, pos_function)

    serve_elements = find_elements(driver, "test_ExpoCell_BODY")

    double_click_the_button(driver, element=serve_elements[int(num) - 1])


@step("POS {pos_function} stores order id")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)
    id_element = find_elements(driver, "test_SaleHeader_TEXT")
    id_text = id_element[0].text.split(" ")[2]
    store_order_number(id_text)


@step("POS {pos_function} checks if order count increases by {amount}")
def step_impl(context, pos_function, amount):
    global stored_order_count

    driver = driver_options(context, pos_function)
    count_element = find_elements(driver, "test_StatisticsRender_ORDERS-COUNT")
    current_count = int(count_element[0].text.split(" ")[-1])
    if (int(stored_order_count) + int(amount)) != current_count:
        raise Exception("Order count did not increase by {}".format(amount))


@step("POS {pos_function} stores order count")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)
    count_element = find_elements(driver, "test_StatisticsRender_ORDERS-COUNT")
    count_text = count_element[0].text.split(" ")[-1]
    store_order_count(count_text)


@step("KDS {pos_function} checks if order's operator is {operator}")
def step_impl(context, pos_function, operator):
    driver = driver_options(context, pos_function)
    operator_element = find_elements(driver, "test_KdsCell_FOOTER")
    if operator != operator_element[0].text.split(" ")[1].replace("\n", "").replace(")", ""):
        raise Exception("Values didn't match!")


@step("KDS {pos_function} checks cell footer order number")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)

    cell_footer_element = find_elements(driver, "test_KdsCell_FOOTER")
    check_result = check_order_number(cell_footer_element[0].text.replace("\n", "").split(" ")[-1])
    if not check_result:
        raise Exception("Values didn't match!")


@step("KDS {pos_function} checks if order {contains} contains tag {tag}")
def step_impl(context, pos_function, contains, tag):
    driver = driver_options(context, pos_function)

    tag_elements = find_elements(driver, "test_Cell_{}".format(tag))

    if contains.lower() == 'does' and not tag_elements:
        raise Exception("Tag did not contain {}".format(tag))

    elif contains.lower() in ["doesn't", "does not", "doesnt"] and tag_elements:
        raise Exception("Tag contained {}".format(tag))


@step("KDS {pos_function} checks if there's a canceled order")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)

    canceled_cell = find_elements(driver, "//div[contains(@class, 'canceledOrder_true')]", find_type=By.XPATH)

    if not canceled_cell:
        raise Exception("There wasn't any canceled order!")


@step("KDS {pos_function} checks if kds cell is blinking")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)

    blinking_state = find_elements(driver, "//div[contains(@class, 'all_ready_true')]", find_type=By.XPATH)

    if not blinking_state:

        raise Exception("There wasn't any blinking order!")


@step("PICKUP waits order threshold")
def step_impl(context):

    kds_loader = eTree.parse(os.environ["KDSLOADER"])
    root = kds_loader.getroot()

    threshold_1 = list(root.find(".//*[@name='Threshold01']"))[0].text.split('#')[0].split(':')
    threshold_1_seconds = (int(threshold_1[0]) * 3600) + (int(threshold_1[1]) * 60) + (int(threshold_1[2]))

    time.sleep(threshold_1_seconds)


@step("PICKUP checks order in Ready Box")
def step_impl(context):
    driver = driver_options(context, 'pickup')

    box_element = find_elements(driver, "test_OrdersBox_{}".format(stored_order_number))

    if not box_element:
        raise Exception("Values didn't match!")


@step("PICKUP checks if stored order is not on screen")
def step_impl(context):
    global stored_order_number

    driver = driver_options(context, 'pickup')

    element_path = "//*[text()='{}']".format(stored_order_number)
    element_result = find_elements(driver, element_path, find_type=By.XPATH, mandatory=True)

    if element_result:
        raise Exception("Stored id is on screen!")


@step("PICKUP waits pickup thresholds")
def step_impl(context):
    driver = driver_options(context, 'pickup')

    kds_loader = eTree.parse(os.environ["KDSLOADER"])
    root = kds_loader.getroot()

    threshold_1 = list(root.find(".//*[@descr='Pickup threshold 1']"))[0].text.split(':')
    threshold_1_seconds = (int(threshold_1[0]) * 3600) + (int(threshold_1[1]) * 60) + (int(threshold_1[2]))

    threshold_3 = list(root.find(".//*[@descr='Pickup threshold 3']"))[0].text.split(':')
    threshold_3_seconds = (int(threshold_3[0]) * 3600) + (int(threshold_3[1]) * 60) + (int(threshold_3[2]))

    ready_box_element = find_elements(driver, "test_ReadyOrdersBox_0")

    if not check_order_number(ready_box_element[0].text):
        raise Exception("Order ID not found at ready box!")

    time.sleep(threshold_1_seconds)

    called_box_element = find_elements(driver, "test_CalledOrderBox_0")

    if not check_order_number(called_box_element[0].text):
        raise Exception("Order ID not found at called box!")

    time.sleep(threshold_3_seconds)

    called_box_element = find_elements(driver, "test_CalledOrderBox_0")

    if check_order_number(called_box_element[0].text):
        raise Exception("Order ID not removed!")


@step("POS PICKUP waits auto order command")
def step_impl(context):
    driver = driver_options(context, "PICKUP")

    kds_loader = eTree.parse(os.environ["NKDSLOADER"])
    root = kds_loader.getroot()
    autocommand = list(root.find(".//*[@name='PICKUP']").find(".//*[@name='AutoOrderCommand']").iter('string'))

    if len(autocommand) > 0:
        time_list = autocommand[0].text.split('|')[0].split(':')
        autocommand_in_seconds = (int(time_list[0]) * 3600) + (int(time_list[1]) * 60) + (int(time_list[2]))

        time.sleep(autocommand_in_seconds)

        box_element = find_elements(driver, "test_OrdersBox_{}".format(stored_order_number))

        if box_element:
            raise Exception("Order still on screen")

    else:
        raise Exception("Command time not found")


@step("POS {pos_function} stores footer counter value")
def step_impl(context, pos_function):
    driver = driver_options(context, pos_function)
    footer_counter = find_elements(driver, "//div[contains(@class, 'test_FooterRenderer_LEFT')]", find_type=By.XPATH)
    counter_value = footer_counter[0].text.replace(" ", "")[-1]
    store_footer_counter(int(counter_value))


@step("POS {pos_function} checks if footer counter was increased by {number}")
def step_impl(context, pos_function, number):
    global stored_footer_counter

    driver = driver_options(context, pos_function)
    footer_counter = find_elements(driver, "//div[contains(@class, 'test_FooterRenderer_LEFT')]", find_type=By.XPATH)
    counter_value = int(footer_counter[0].text.replace(" ", "")[-1])
    if counter_value != (stored_footer_counter + int(number)):
        raise Exception("Footer counter was not increased by {}".format(number))


def store_footer_counter(value):
    global stored_footer_counter
    stored_footer_counter = value


def get_zoom_level(driver):
    footer_center = find_elements(driver, "test_FooterRenderer_CENTER", mandatory=True)

    footer_text = footer_center[0].text

    return footer_text.split(' ')[-1]


def check_order_threshold(driver, threshold_number, order_number=0):
    kds_containers = find_elements(driver, "test_KdsCell_CONTAINER", mandatory=True)

    return 'threshold_{}'.format(threshold_number) in kds_containers[int(order_number)].text


def store_order_number(number):
    global stored_order_number

    stored_order_number = number


def store_order_count(number):
    global stored_order_count

    stored_order_count = number


def check_order_number(number):
    return stored_order_number == number


def store_customer_name(name):
    global stored_customer_name

    stored_customer_name = name


def check_customer_name(name):
    return stored_customer_name == name
