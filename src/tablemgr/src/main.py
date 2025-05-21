# -*- coding: utf-8 -*-

import os
import component
from debug_helper import import_pydevd
from helper import config_logger


def main():
    import_pydevd(os.environ["LOADERCFG"], 9134)
    config_logger(os.environ["LOADERCFG"], "TableManager")

    component.main()
