import importlib
import logging
import os
from os.path import dirname, isfile, join

from msgbus import MBEasyContext

mb_context = None  # type: MBEasyContext
logger = logging.getLogger("PosActions")

USECS_PER_SEC = 1000000

# Custom Model Keys
SIGNED_IN_USER = "SIGNED_IN_USER"

pos_config = None


class PosConfig(object):
    def __init__(self, max_transfer_value, skim_digit_limit, sangria_levels, auto_generate_skim_number, store_id, min_value_to_ask_bordereau_justify_config):
        self.max_transfer_value = max_transfer_value
        self.skim_digit_limit = skim_digit_limit
        self.sangria_levels = sangria_levels
        self.auto_generate_skim_number = auto_generate_skim_number
        self.store_id = store_id
        self.min_value_to_ask_bordereau_justify_config = min_value_to_ask_bordereau_justify_config


def is_table(pos_id):
    return True


def get_pos_service(pos_id):
    return "POS{}".format(pos_id)


def get_operator(model, user_id):
    for op in model.findall('Operator'):
        if op.get("id") == user_id:
            return op


def get_paused_operator(model):
    for op in model.findall('Operator'):
        if op.get("state") == "PAUSED":
            return op

    return None


def get_all_modules():
    mods = []
    for dirpath, dirnames, filenames in os.walk(dirname(__file__)):
        if dirpath == dirname(__file__):
            continue

        if dirpath == join(dirname(__file__), "util"):
            continue
        if dirpath == join(dirname(__file__), "models"):
            continue

        for filename in filenames:
            if isfile(join(dirpath, filename)) and not filename.endswith("__init__.py") and filename.endswith(".py"):
                mods.append(
                    "actions." + join(dirpath, filename)[len(dirname(__file__)) + 1:].replace(os.path.sep, '.')[:-3])
    return mods


def get_all_util_modules():
    mods = []
    for dirpath, dirnames, filenames in os.walk(dirname(__file__)):
        if dirpath == dirname(__file__):
            continue

        if dirpath != join(dirname(__file__), "util"):
            continue
        if dirpath != join(dirname(__file__), "models"):
            continue

        for filename in filenames:
            if isfile(join(dirpath, filename)) and not filename.endswith("__init__.py") and filename.endswith(".py"):
                mods.append(
                    "actions." + join(dirpath, filename)[len(dirname(__file__)) + 1:].replace(os.path.sep, '.')[:-3])
    return mods


def import_all_modules():
    for module in modules:
        importlib.import_module(module)


def import_all_util_modules():
    for module in util_modules:
        importlib.import_module(module)


modules = get_all_modules()
util_modules = get_all_util_modules()
import_all_modules()


def set_mb_context(mb_context_param):
    global mb_context
    mb_context = mb_context_param
    # for m in modules:
    #    reload(importlib.import_module(m))


def set_pos_config(pos_config_param):
    # type: (PosConfig) -> None
    global pos_config
    pos_config = pos_config_param
    for m in modules:
        reload(importlib.import_module(m))
    for m in util_modules:
        reload(importlib.import_module(m))
