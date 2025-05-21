# -*- coding: utf-8 -*-

import time

from xml.etree import cElementTree as eTree
from threading import Thread

from mbcontextmessagehandler import MbContextMessageBus
from messagebus import Message, DataType
from msgbus import TK_SYS_ACK, MBException, TK_REPORT_GENERATE, TK_PRN_PRINT, TK_POS_GETMODEL


class Printer(object):
    def __init__(self, mb_context, pos_id, logger, pos_list=[]):
        self.message_bus = MbContextMessageBus(mb_context)
        self.pos_id = str(pos_id)
        self.logger = logger
        self.pos_list = pos_list
        self.remote_order_pos_model = self._get_model()
        self.printer_service = self._get_printer_service()

    def print_delivery_report(self, order_id):
        # type: () -> None
        params = self.pos_id + "\0" + str(order_id) + "\0" + ','.join(str(x) for x in self.pos_list)
        self._print("deliveryreport", params)

    def _print(self, report_name, params):
        print_thread = Thread(target=self._printer_retry, args=(report_name, params))
        print_thread.daemon = True
        print_thread.start()

    def _printer_retry(self, report_name, params):
        # type: () -> None
        retry = 0
        while retry < 5:
            try:
                report_text = self._generate_report(report_name, params)
                if report_text:
                    response = self.print_report_text(report_text)
                    if response:
                        self.logger.info("Success printing received data")
                        break
            except MBException as _:
                self.logger.error("Error printing received data")
        
            time.sleep(0.75)
            retry += 1
            self.logger.error("Retry number: {}".format(retry))

    def _generate_report(self, report_name, params):
        data = "%s\0%s" % (report_name, params)
        message = Message(token=TK_REPORT_GENERATE,
                          data=data,
                          data_type=DataType.param,
                          timeout=50 * 1000000)
    
        msg = self.message_bus.send_message("ReportsGenerator", message)
        if msg.token == TK_SYS_ACK:
            return msg.data

    def print_report_text(self, report_text):
        # type: (str) -> bool
        message = Message(token=TK_PRN_PRINT,
                          data=report_text,
                          data_type=DataType.string,
                          timeout=10 * 1000000)
    
        res = self.message_bus.send_message(self.printer_service, message)
        if res.token != TK_SYS_ACK:
            self.logger.error("Failed to print delivery report")
            return False
    
        return True

    def _get_printer_service(self):
        # type: () -> str
        services = [node for node in self.remote_order_pos_model.findall("UsedServices/Service")
                    if node.get("type") == "printer"]
    
        for service in services:
            if service.get("default") == "true":
                return str(service.get("name"))

    def _get_model(self):
        # type: () -> eTree.ElementTree
        message = Message(token=TK_POS_GETMODEL,
                          data=str(self.pos_id),
                          data_type=DataType.string,
                          timeout=10 * 1000000)
    
        res = self.message_bus.send_message("POS{}".format(self.pos_id), message)
    
        if res.token != TK_SYS_ACK:
            raise Exception("Could not retrieve remote order pos model. POS #{}".format(self.pos_id))
    
        return eTree.XML(res.data)
