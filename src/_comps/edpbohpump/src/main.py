# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\kernel\bohpump\main.py
import os
from helper import import_pydevd, config_logger


def main():
    loader_cfg = os.environ["LOADERCFG"]
    import_pydevd(loader_cfg, 9136, False)
    config_logger(loader_cfg, "BohPump")
    import bohpump
    bohpump.main()
