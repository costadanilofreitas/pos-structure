# -*- coding: utf-8 -*-
from kdsmonitor import KdsMonitor
from messagehandler import EventHandler
from msgbus import TK_SYS_NAK, TK_SYS_ACK, MBEasyContext, MBException, TK_KDS_GETMODEL, FM_PARAM
from bustoken import TK_KDSMONITOR_STATUS_REQUEST
from xml.etree import cElementTree as eTree
import ast


class KdsMonitorEventHandler(EventHandler):
    def __init__(self, mbcontext, kds_monitor_thread):
        # type: (MBEasyContext, KdsMonitor) -> None
        super(KdsMonitorEventHandler, self).__init__(mbcontext)
        self.kds_monitor_thread = kds_monitor_thread

    def get_handled_tokens(self):
        return [TK_KDSMONITOR_STATUS_REQUEST]

    def handle_message(self, msg):
        try:
            if msg.token == TK_KDSMONITOR_STATUS_REQUEST:
                response = self._handle_status_request(msg)
            else:
                response = (False, "")

            msg.token = TK_SYS_ACK if response[0] else TK_SYS_NAK
            self.mbcontext.MB_ReplyMessage(msg, data=response[1])

        except Exception as ex:
            # sys_log_exception("Unexpected exception when handling event {0}. Error message: {1}".format(msg.token, ex.message))
            msg.token = TK_SYS_NAK
            self.mbcontext.MB_ReplyMessage(msg, data=str(ex))

        return False

    def handle_event(self, subject, evt_type, data, msg):
        raise NotImplementedError()

    def _handle_status_request(self, msg):
        try:
            model_msg = self.mbcontext.MB_EasySendMessage("KdsController", TK_KDS_GETMODEL, format=FM_PARAM, data="1", timeout=10000 * 1000)
            model_tree = eTree.XML(model_msg.data)
            kdss_elements = model_tree.find("KDSs").findall('KDS')
            kds_status_list = []
            kds_info = []
            for kds in self.kds_monitor_thread.kdss_to_monitor:
                kds_id = (str(kds.name)).strip("KDS")
                for kds_element in kdss_elements:
                    kds_element_id = kds_element.get('id')
                    if kds_id == kds_element_id:
                        kds_info.append(kds_id)
                        kds_info.append(kds_element.get('desc'))
                        if kds.enabled:
                            kds_info.append("Enabled")
                        else:
                            kds_info.append("Disabled")
                        kds_status_list.append(kds_info)
                        kds_info = []
                        break
            return True, str(kds_status_list)
        except MBException as ex:
            return False, "Erro ao procurar KDSs"

    def terminate_event(self):
        self.kds_monitor_thread.finish()
