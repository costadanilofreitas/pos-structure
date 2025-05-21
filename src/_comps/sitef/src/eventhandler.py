# -*- coding: utf-8 -*-
import threading
import logging

from messagehandler import EventHandler
from bustoken import \
    TK_SITEF_ADD_PAYMENT, \
    TK_SITEF_CANCEL_PAYMENT, \
    TK_SITEF_FINISH_PAYMENT, \
    TK_SITEF_CONNECTIVITY_TEST, \
    TK_SITEF_AVAILABLE
from systools import sys_log_exception
from msgbus import TK_SYS_NAK, TK_SYS_ACK
from model import Event
from time import sleep

code_received = False
secu_code = ""


class SitefEventHandler(EventHandler):
    def __init__(self, mbcontext, sitef_processor):
        super(SitefEventHandler, self).__init__(mbcontext)
        self.sitef_processor = sitef_processor
        self._processing = False
        self.logger = logging.getLogger("Sitef")
        self.logger.info('[SitefEventHandler] __init__')
        self._lock = threading.Lock()

    def get_handled_tokens(self):
        return [TK_SITEF_ADD_PAYMENT, TK_SITEF_CANCEL_PAYMENT, TK_SITEF_FINISH_PAYMENT, TK_SITEF_CONNECTIVITY_TEST]

    def handle_message(self, msg):
        global code_received, secu_code
        try:
            code_received = True
            secu_code = ""

            if msg.token == TK_SITEF_ADD_PAYMENT:
                code_received = False
                if self._processing:
                    msg.token = TK_SYS_NAK
                    self.mbcontext.MB_ReplyMessage(msg, data=None)
                else:
                    with self._lock:
                        self._processing = True
                    pos_id = msg.data.split(';')[0]
                    try:
                        self._handle_add_payment(msg)
                    finally:
                        with self._lock:
                            self._processing = False

                        # Send EVENT to notify SITEF FINISHED...
                        self.mbcontext.MB_EasyEvtSend('SITEF', 'PROCESS_FINISHED', xml='', sourceid=int(pos_id), synchronous=True)

            elif msg.token == TK_SITEF_CANCEL_PAYMENT:
                self._handle_cancel_payment(msg)

            elif msg.token == TK_SITEF_FINISH_PAYMENT:
                self.logger.info('[SitefEventHandler] received msg: TK_SITEF_FINISH_PAYMENT')
                self._handle_finish_payment(msg)

            elif msg.token == TK_SITEF_CONNECTIVITY_TEST:
                self._handle_connectivity_test(msg)

            elif msg.token == TK_SITEF_AVAILABLE:
                self._handle_sitef_available(msg)

            else:
                self.logger.error('[SitefEventHandler] error receiving msg')
                msg.token = TK_SYS_NAK
                self.mbcontext.MB_ReplyMessage(msg)

        except Exception as ex:
            self.logger.exception('[SitefEventHandler] Exception: {}'.format(ex))
            sys_log_exception("Unexpected exception when handling event {0}. Error message: {1}".format(msg.token, str(ex)))
            msg.token = TK_SYS_NAK
            self.mbcontext.MB_ReplyMessage(msg)

    def handle_event(self, subject, evt_type, data, msg):
        global code_received, secu_code
        self.logger.info('[SitefEventHandler] event: ({}|{})'.format(subject, data))
        if subject == 'SITEF' and evt_type == 'totemReturnKeyboard':
            code_received = True
            secu_code = data

    def terminate_event(self):
        self.sitef_processor.terminate()

    def _handle_add_payment(self, msg):
        params = msg.data.split(';')
        posid, orderid, operador, tender_type, amount, data_fiscal, hora_fiscal, tender_seq_id, display_via_api = params

        self.sitef_processor.sitef_service_finder.lock_sitef()
        result, data = self.sitef_processor.process(msg, posid, orderid, operador, tender_type, amount, data_fiscal, hora_fiscal, tender_seq_id, display_via_api, None)
        self.sitef_processor.sitef_service_finder.release_sitef()
        if result:
            msg.token = TK_SYS_ACK
            msg.data = data
        else:
            msg.token = TK_SYS_NAK
        self.mbcontext.MB_ReplyMessage(msg, data=msg.data)

    def _handle_cancel_payment(self, msg):
        self.sitef_processor.cancel()
        msg.token = TK_SYS_ACK
        self.mbcontext.MB_ReplyMessage(msg, data=msg.data)

    def _handle_finish_payment(self, msg):
        posid, orderid, data_fiscal, hora_fiscal, status = msg.data.split(';')
        msg.data = self.sitef_processor.finalizar(posid, orderid, data_fiscal, hora_fiscal, int(status))
        msg.token = TK_SYS_ACK
        self.mbcontext.MB_ReplyMessage(msg, data=msg.data)

    def _handle_connectivity_test(self, msg):
        posid, data_fiscal, hora_fiscal = msg.data.split(';')
        try:
            msg.data = self.sitef_processor.process(msg, posid, "", "", "3", "", data_fiscal, hora_fiscal, "", True, None)[1]
            msg.token = TK_SYS_ACK
            self.mbcontext.MB_ReplyMessage(msg, data=msg.data)
        except Exception:
            msg.data = "Erro ao tentar conexão com SiTef"
            msg.token = TK_SYS_NAK
            self.mbcontext.MB_ReplyMessage(msg, data=msg.data)

    def _handle_sitef_available(self, msg):
        msg.token = TK_SYS_ACK
        self.mbcontext.MB_EasyReplyMessage(msg)


class SitefCallback(object):
    def __init__(self, mbcontext):
        self.mbcontext = mbcontext
        self.logger = logging.getLogger('Sitef')
        self.logger.info('[SitefCallback] __init__')

    def callback(self, pos_id, message, display_via_api, wait_operator=False):
        global code_received, secu_code
        parsed_message = message.split('|')
        message = parsed_message[0]
        if message == "THREAD_ASK_PIN":
            if display_via_api:
                code_received = False
                self.logger.info('[SitefCallback] will ask info ({}|{})'.format(pos_id, message))
                self.mbcontext.MB_EasyEvtSend('TOTEM', Event.totemShowKeyboard, "{}|{}".format(pos_id, parsed_message[1]))
                polling_cnt = 40
                while not code_received and polling_cnt > 0:
                    sleep(0.5)
                self.logger.info('[SitefCallback] result: ({}|{})'.format(pos_id, secu_code))
                pin = secu_code if secu_code else None
                code_received = False
            else:
                from sysactions import show_keyboard
                pin = show_keyboard(pos_id, "Digite o Código de Segurança do Cartão", title="Código de Segurança", mask="INTEGER", numpad=True)
            pin = "CANCELA" if pin is None else pin

            return str(pin)
        else:
            if display_via_api:
                message = "{}|{}".format(pos_id, message)
                self.logger.info('[SitefCallback] will show message ({})'.format(message))
                self.mbcontext.MB_EasyEvtSend('TOTEM', Event.totemShowMessageBox, "%s" % message)
            else:
                if wait_operator:
                    from sysactions import show_messagebox
                    show_messagebox(pos_id, "%s" % message, title="Informação", icon="info", buttons="Ok")
                elif message != "":
                    data = ";".join([message, pos_id])
                    self.mbcontext.MB_EasyEvtSend(Event.sitefStatusUpdate, "STATUS_UPDATE", data)
    # END callback
