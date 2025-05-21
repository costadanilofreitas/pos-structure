# -*- coding: utf-8 -*-

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as exp_cond
from selenium.webdriver.support.ui import WebDriverWait

DEFAULT_TIMEOUT = 3


def find_elements(driver, path, mandatory=True, find_type=By.CLASS_NAME, timeout=DEFAULT_TIMEOUT):
    elements = None
    try:
        elements = WebDriverWait(driver, timeout).until(exp_cond.presence_of_all_elements_located((find_type, path)))
        if len(elements) == 1:
            return elements[0]
        return elements
    except TimeoutException:
        if mandatory:
            raise Exception("Element not found. Path: {}; FindType: {}; Timeout: {}".format(path, find_type, timeout))
    finally:
        return elements


def get_element_when_clickable(driver, path=None, element=None, find_type=By.CLASS_NAME, timeout=DEFAULT_TIMEOUT):
    if element:
        return element
    elif path:
        return WebDriverWait(driver, timeout).until(exp_cond.element_to_be_clickable((find_type, path)))
    else:
        raise Exception("Need to give the element object or the element path")


def click_the_button(driver, path=None, element=None, find_type=By.CLASS_NAME, timeout=DEFAULT_TIMEOUT):
    element = get_element_when_clickable(driver, path, element, find_type, timeout)
    element.click()
    return element


def double_click_the_button(driver, path=None, element=None, find_type=By.CLASS_NAME, timeout=DEFAULT_TIMEOUT):
    element = get_element_when_clickable(driver, path, element, find_type, timeout)
    ActionChains(driver).double_click(element).perform()
    return element


def send_keys_to_input(driver, keys_to_press, path="//input", find_type=By.CLASS_NAME, timeout=DEFAULT_TIMEOUT):
    element = click_the_button(driver, path, find_type=find_type, timeout=timeout)
    element.send_keys(keys_to_press)
    return element
