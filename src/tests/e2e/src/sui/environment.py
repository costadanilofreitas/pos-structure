# -*- coding: utf-8 -*-

import os
import platform

import mwposdriver
from helper.sqlite_helper import set_db_path
from mw.common.msgbus import MBEasyContext
from selenium import webdriver

# Select the Web Driver used to tests: Chrome|PhantomJS
WEB_DRIVER = "Chrome"


def before_all(context):
    _set_context_directories(context)
    _set_os_environments(context)
    _set_mb_context(context)
    _start_mw_pos_driver(context)
    # _start_web_driver(context)


def after_all(context):
    if context.is_release and context.mw_pos_driver.is_running():
        context.mw_pos_driver.terminate_pos()

    driver = _get_context_driver(context)

    if driver:
        driver.quit()


def before_scenario(context, scenario):
    context.scenario_name = scenario.name


def after_step(context, step):
    if step.status.name == 'failed':

        driver = _get_context_driver(context)
        
        if driver:
            driver.save_screenshot(os.path.join("screenshots", context.scenario_name, "{}.png".format(step.name)))
            driver.quit()


def _get_context_driver(context):
    driver = None
    
    if 'pos_qsr_fl_fl' in context._stack[0]:
        driver = context.pos_qsr_fl_fl

    elif 'pos_qsr_fc_ot' in context._stack[0]:
        driver = context.pos_qsr_fc_ot

    elif 'pos_qsr_fc_cs' in context._stack[0]:
        driver = context.pos_qsr_fc_cs

    elif 'pos_ts_fl_fl' in context._stack[0]:
        driver = context.pos_ts_fl_fl

    elif 'pos_ts_ts_fl' in context._stack[0]:
        driver = context.pos_ts_ts_fl

    elif 'pos_ts_fl_cs' in context._stack[0]:
        driver = context.pos_ts_fl_cs

    elif 'expo' in context._stack[0]:
        driver = context.expo

    elif 'prep_frito' in context._stack[0]:
        driver = context.prep_frito

    elif 'prep_chapa' in context._stack[0]:
        driver = context.prep_chapa

    elif 'kds_grelha' in context._stack[0]:
        driver = context.kds_grelha

    elif 'totem' in context._stack[0]:
        driver = context.totem

    elif 'pickup' in context._stack[0]:
        driver = context.pickup

    return driver


def _start_web_driver(context):
    if WEB_DRIVER.lower() == "chrome":
        context.pos_driver = get_chrome_driver_webdriver(1, context)
    elif WEB_DRIVER.lower() == "phantomjs":
        context.pos_driver = get_phantom_webdriver(1, context)


def _set_mb_context(context):
    context.mb_context = MBEasyContext("End2EndTests")


def _start_mw_pos_driver(context):
    context.mw_pos_driver = mwposdriver.MwPosDriver(os.path.abspath(context.bin_dir), os.path.abspath(context.data_dir))
    context.is_release = "RELEASE" in os.environ and os.environ["RELEASE"] == "true"
    if context.is_release:
        if context.mw_pos_driver.is_running():
            raise Exception("HyperVisor is already running")

        context.mw_pos_driver.delete_all_databases()
        context.mw_pos_driver.start_pos()

    elif not context.mw_pos_driver.is_running():
        context.mw_pos_driver.start_pos()


def _set_os_environments(context):
    if "BIN_PATH" not in os.environ:
        os.environ["BIN_PATH"] = context.bin_dir
    if "DATA_PATH" not in os.environ:
        os.environ["DATA_PATH"] = context.data_dir
    os.environ["PATH"] = os.environ["PATH"] + ";" + os.environ["BIN_PATH"]
    os.environ["PATH"] = os.environ["PATH"] + ";" + _get_phantomjs_folder(context)
    os.environ["PATH"] = os.environ["PATH"] + ";" + _get_chrome_driver_folder(context)
    os.environ["HVPORT"] = "14000"
    os.environ["HVIP"] = "127.0.0.1"
    os.environ["HVCOMPPORT"] = "35686"
    os.environ["PYLOADER"] = os.path.join(context.sdk_dir, "datas\\server\\bundles\\pyscripts\\loader.cfg")
    os.environ["KDSLOADER"] = os.path.join(context.sdk_dir, "datas\\server\\bundles\\kdsctrl\\loader.cfg")
    os.environ["NKDSLOADER"] = os.path.join(context.sdk_dir, "datas\\server\\bundles\\nkdsctrl\\loader.cfg")
    os.environ["POSCTRL"] = os.path.join(context.sdk_dir, "datas\\server\\bundles\\posctrl")
    os.environ["STORECFGLOADER"] = os.path.join(context.sdk_dir, "datas\\server\\bundles\\storecfg\\loader.cfg")
    os.chdir = (os.path.abspath(context.bin_dir))


def _set_context_directories(context):
    context.sdk_dir = os.path.abspath(os.path.join(os.path.realpath(__file__), "..", "..", "..", "..", "..", ".."))
    context.sys_platform = "linux" if platform.system() == "Linux" else "windows"

    if context.sys_platform == "windows":
        context.bin_dir = os.path.join(context.sdk_dir, "mwsdk", "windows-x86", "bin")

    elif context.sys_platform == "linux":
        context.bin_dir = os.path.join(context.sdk_dir, "mwsdk", "linux-centos-x86_64", "bin")

    context.data_dir = os.path.join(context.sdk_dir, "datas", "server")
    context.database_dir = os.path.join(context.data_dir, "databases")

    set_db_path(context.database_dir)


def _get_chrome_driver_folder(context):
    return os.path.abspath(os.path.join("lib", "chromedriver", context.sys_platform))


def _get_chrome_driver_path(context):
    return os.path.abspath(os.path.join(_get_chrome_driver_folder(context), "chromedriver"))


def _get_phantomjs_folder(context):
    return os.path.abspath(os.path.join("lib", "phantomjs", context.sys_platform))


def _get_phantomjs_path(context):
    return os.path.abspath(os.path.join(_get_phantomjs_folder(context), "phantomjs"))


def get_phantom_webdriver(pos_id, context, mode="Desktop"):
    driver = webdriver.PhantomJS(_get_phantomjs_path(context))
    driver.set_window_size(1024, 768)

    if mode.lower() == 'desktop':
        driver.get("http://localhost:8080/sui/?posid={}".format(pos_id))

    elif mode.lower() == 'mobile':
        driver.get("http://localhost:8080/sui/?posid={}".format(pos_id) + '&mobile=true')

    elif mode.lower() == 'totem':
        driver.get("http://127.0.0.1:8080/sui/?posid={}".format(pos_id) + '&totem=true')

    elif mode.lower() == 'kui':
        driver.get("http://localhost:8080/kui/?kdsid={}".format(pos_id))

    else:
        raise Exception("Mode not defined!")

    return driver


def get_chrome_driver_webdriver(pos_id, context, mode="Desktop"):
    options = webdriver.ChromeOptions()
    options.add_experimental_option('w3c', False)

    driver = webdriver.Chrome(_get_chrome_driver_path(context), chrome_options=options)
    driver.set_window_size(1024, 768)

    if mode.lower() == 'desktop':
        driver.get("http://localhost:8080/sui/?posid={}".format(pos_id))

    elif mode.lower() == 'mobile':
        driver.get("http://localhost:8080/sui/?posid={}".format(pos_id) + '&mobile=true')

    elif mode.lower() == 'totem':
        driver.get("http://127.0.0.1:8080/sui/?posid={}".format(pos_id) + '&totem=true')

    elif mode.lower() == 'kui':
        driver.get("http://localhost:8080/kui/?kdsid={}".format(pos_id))

    else:
        raise Exception("Mode not defined!")

    return driver
