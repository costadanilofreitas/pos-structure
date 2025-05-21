import sys
import os
import cfgtools

from cfgtools import Group, Key
from msgbus import MBEasyContext
from messagehandler import MessageHandler
from eventhandler import KdsMonitorEventHandler
from kdsmonitor import KdsMonitor, Kds
from old_helper import config_logger

# COMMENT HERE
debugPath = '../python/pycharm-debug.egg'
if os.path.exists(debugPath):
    try:
        sys.path.index(debugPath)
    except:
        sys.path.append(debugPath)
    import pydevd

# Use the line below in the function you want to debug
# pydevd.settrace('localhost', port=9123, stdoutToServer=True, stderrToServer=True)
# UNTIL HERE

REQUIRED_SERVICES = "ProductionSystem|Persistence"


def main():
    config_logger(os.environ["LOADERCFG"], 'KdsMonitor')

    config = cfgtools.read(os.environ["LOADERCFG"])
    mbcontext = MBEasyContext("KdsMonitor")

    kds_list = []
    kds_group = config.find_group("KdsMonitor.KdsDict")  # type: Group
    for kds_key in kds_group.keys:  # type: Key
        name = kds_key.name
        ip = kds_key.descr
        view_name = str(kds_key.values[0])
        kds = Kds(name, ip, view_name)
        kds_list.append(kds)

    monitor_interval = int(config.find_value("KdsMonitor.MonitorInterval") or "15")
    max_error_count = int(config.find_value("KdsMonitor.MaxErrorCount") or "3")
    start_wait_time = int(config.find_value("KdsMonitor.StartWaitTime") or "120")

    kds_monitor_thread = KdsMonitor(mbcontext, kds_list, monitor_interval, max_error_count, start_wait_time)
    kds_monitor_thread.daemon = True

    kds_monitor_event_handler = KdsMonitorEventHandler(mbcontext, kds_monitor_thread)
    kds_message_handler = MessageHandler(mbcontext, "KdsMonitor", "KdsMonitor", REQUIRED_SERVICES, kds_monitor_event_handler)

    kds_monitor_thread.start()
    kds_message_handler.handle_events()
