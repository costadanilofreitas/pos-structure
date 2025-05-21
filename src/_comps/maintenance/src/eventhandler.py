import logging

from bustoken import TK_MAINTENANCE_TERMINATE_REQUEST, TK_MAINTENANCE_RESTART_REQUEST, \
    TK_MAINTENANCE_RECREATE_FILES_XML, TK_MAINTENANCE_RECREATE_FILE_NUMBER, TK_MAINTENANCE_CLEAN_AUDIT_LOG
from messagehandler import EventHandler
from msgbus import MBEasyContext, TK_SYS_ACK, TK_SYS_NAK
from systools import sys_log_exception

from events import MaintenanceProcessor, CleanDatabasesProcessor, CleanJsonProcessors

logger = logging.getLogger("Maintenance")


class MaintenanceEventHandler(EventHandler):
    def __init__(self, mbcontext, maintenance_processor,  clean_databases_processor, clean_json_processor):
        # type: (MBEasyContext, MaintenanceProcessor, CleanDatabasesProcessor, CleanJsonProcessors) -> None
        super(MaintenanceEventHandler, self).__init__(mbcontext)
        self.mbcontext = mbcontext
        self.maintenance_processor = maintenance_processor
        self.clean_databases_processor = clean_databases_processor
        self.clean_json_processor = clean_json_processor

    def subscrive_events(self, subject):
        pass

    def terminate_event(self):
        pass

    def get_handled_tokens(self):
        return [TK_MAINTENANCE_TERMINATE_REQUEST,
                TK_MAINTENANCE_RESTART_REQUEST,
                TK_MAINTENANCE_RECREATE_FILES_XML,
                TK_MAINTENANCE_RECREATE_FILE_NUMBER]

    def handle_event(self, subject, evt_type, data, msg):
        logger.info("Event received: [{}]".format(subject))
        if not self.maintenance_processor.is_inside_maintenance_window():
            logger.info("Not inside maintenance window. Exiting...")
            return

        if subject == "CleanDatabases":
            self.clean_databases_processor.clean_databases()
        elif subject == "VacuumDatabases":
            self.clean_databases_processor.vacuum_databases()
        elif subject == "CleanJson":
            self.clean_json_processor.clean_json()

    def handle_message(self, msg):
        try:
            if msg.token == TK_MAINTENANCE_TERMINATE_REQUEST:
                response = self.maintenance_processor.handle_terminate_request(msg)
            elif msg.token == TK_MAINTENANCE_RESTART_REQUEST:
                response = self.maintenance_processor.handle_restart_request(msg)
            elif msg.token == TK_MAINTENANCE_CLEAN_AUDIT_LOG:
                response = self.maintenance_processor.clean_audit_log(msg)
            else:
                response = (False, "")

            msg.token = TK_SYS_ACK if response[0] else TK_SYS_NAK
            self.mbcontext.MB_ReplyMessage(msg, data=response[1])
        except Exception as ex:
            sys_log_exception("Unexpected exception handling event: {}".format(msg.token))
            msg.token = TK_SYS_NAK
            self.mbcontext.MB_ReplyMessage(msg, data=str(ex))
