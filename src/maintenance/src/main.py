# -*- coding: utf-8 -*-

import os

import cfgtools
import pyscripts
from helper import config_logger, import_pydevd
from messagehandler import MessageHandler
from msgbus import MBEasyContext
from systools import sys_parsefilepath

from eventhandler import MaintenanceEventHandler
from events import MaintenanceProcessor, CleanDatabasesProcessor, CleanJsonProcessors


def main():
    import_pydevd(os.environ["LOADERCFG"], 9128)

    required_services = "StoreWideConfig|Persistence|PosController"

    config_logger(os.environ["LOADERCFG"], 'Maintenance')
    config = cfgtools.read(os.environ["LOADERCFG"])

    mbcontext = MBEasyContext("MaintenanceComp")
    pyscripts.mbcontext = mbcontext

    start_hour = int(config.find_value("MaintenanceComponent.StartHour", default=5))
    end_hour = int(config.find_value("MaintenanceComponent.EndHour", default=6))

    comp_no = int(config.find_value("MaintenanceComponent.Number"))

    files_to_delete = config.find_values("MaintenanceComponent.DeleteFiles") or []
    dirs_to_delete = config.find_values("MaintenanceComponent.DeleteDirs") or []

    maintenance_processor = MaintenanceProcessor(mbcontext, comp_no, start_hour, end_hour)
    clean_databases_processor = None
    clean_json_processors = None
    if comp_no == 0:  # Server
        fiscal_path = sys_parsefilepath(config.find_value("MaintenanceComponent.XmlFiscalPath", default=""))
        fiscal_sent_path = sys_parsefilepath(config.find_value("MaintenanceComponent.XmlFiscalEnviados", default="Enviados"))
        json_paths = config.find_values("MaintenanceComponent.JsonPaths") or []
        keep_days = int(config.find_value("MaintenanceComponent.JsonKeepDays", default=90))
        days_to_keep_orders_on_databases = int(config.find_value("MaintenanceComponent.DaysToKeepOrdersOnDatabases", default=90))
        audit_path = sys_parsefilepath(config.find_value("MaintenanceComponent.AuditLogPath"))
        days_to_purge_audit_log = config.find_value("MaintenanceComponent.DaysToKeepAuditLogFiles", default=90)

        maintenance_processor.set_server_parameters(fiscal_path, audit_path, fiscal_sent_path, days_to_purge_audit_log)
        clean_databases_processor = CleanDatabasesProcessor(mbcontext, comp_no, days_to_keep_orders_on_databases)
        clean_json_processors = CleanJsonProcessors(json_paths, keep_days)

    maintenance_event_handler = MaintenanceEventHandler(mbcontext,
                                                        maintenance_processor,
                                                        clean_databases_processor,
                                                        clean_json_processors)

    message_handler = MessageHandler(mbcontext,
                                     "Maintenance%02d" % comp_no,
                                     "MaintenanceComp",
                                     required_services,
                                     maintenance_event_handler)

    if comp_no == 0:  # Server
        clean_databases_processor.set_server_parameters(maintenance_processor)

    if files_to_delete:
        maintenance_processor.delete_files(files_to_delete)
    if dirs_to_delete:
        maintenance_processor.delete_dirs(dirs_to_delete)

    message_handler.subscribe_events(["CleanDatabases",
                                      "VacuumDatabases",
                                      "CleanJson"])
    message_handler.handle_events()
