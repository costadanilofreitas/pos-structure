# -*- coding: utf-8 -*-

import logging
import unicodedata
from datetime import datetime, timedelta

from bustoken import TK_SITEF_ADD_PAYMENT, TK_SITEF_FINISH_PAYMENT, TK_SITEF_AVAILABLE
from messagehandler import EventHandler
from msgbus import TK_SYS_NAK, TK_SYS_ACK
from systools import sys_log_exception

logger = logging.getLogger("Cappta")


class CapptaEventHandler(EventHandler):
    def __init__(self, mbcontext, cappta_processor):
        super(CapptaEventHandler, self).__init__(mbcontext)
        self.cappta_processor = cappta_processor

    def get_handled_tokens(self):
        return [TK_SITEF_ADD_PAYMENT, TK_SITEF_FINISH_PAYMENT, TK_SITEF_AVAILABLE]

    def handle_message(self, msg):
        try:
            if msg.token == TK_SITEF_ADD_PAYMENT:
                self._handle_add_payment(msg)
            elif msg.token == TK_SITEF_FINISH_PAYMENT:
                self._handle_finish_payment(msg)
            elif msg.token == TK_SITEF_AVAILABLE:
                self._handle_sitef_available(msg)
            else:
                msg.token = TK_SYS_NAK
                self.mbcontext.MB_ReplyMessage(msg)

        except Exception as ex:
            sys_log_exception("Unexpected exception when handling event {0}. Error message: {1}".format(msg.token, str(ex)))
            msg.token = TK_SYS_NAK
            self.mbcontext.MB_ReplyMessage(msg)

    def handle_event(self, subject, evt_type, data, msg):
        raise NotImplementedError()

    def terminate_event(self):
        pass
    
    def _handle_sitef_available(self, msg):
        msg.token = TK_SYS_ACK
        self.mbcontext.MB_EasyReplyMessage(msg)

    def _handle_add_payment(self, msg):
        posid, orderid, operador, tender_type, amount, data_fiscal, hora_fiscal, tender_seq_id, display_via_api = msg.data.split(';')
        result, msg.data = self.cappta_processor.process(msg, posid, orderid, operador, tender_type, amount, data_fiscal, hora_fiscal, tender_seq_id)
        msg.token = TK_SYS_ACK
        self.mbcontext.MB_ReplyMessage(msg, data=msg.data)

    def _handle_cancel_payment(self, msg):
        msg.data = self.cappta_processor.cancel()
        msg.token = TK_SYS_ACK
        self.mbcontext.MB_ReplyMessage(msg, data=msg.data)

    def _handle_finish_payment(self, msg):
        posid, orderid, data_fiscal, hora_fiscal, status = msg.data.split(';')
        msg.data = self.cappta_processor.finalizar(posid, orderid, data_fiscal, hora_fiscal, int(status))
        msg.token = TK_SYS_ACK
        self.mbcontext.MB_ReplyMessage(msg, data=msg.data)


class CapptaCallback(object):
    def __init__(self, mbcontext):
        self.mbcontext = mbcontext
        self.last_response = dict(message=None, timestamp=None)

    def callback(self, bus_msg, pos_id, response, message):
        from sysactions import show_messagebox, show_keyboard

        try:
            formatted_response = self._format_response(response)

            is_repeated = self._check_if_message_is_not_repeated(response)
            if is_repeated:
                return

            logger.info("Callback -> PosID: {}; Type: {}; Message: {}".format(pos_id, message, formatted_response))
    
            if message == "MENSAGEM":
                data = ";".join([formatted_response, pos_id])
                self.mbcontext.MB_EasyEvtSend("SITEF_STATUS_UPDATE", "STATUS_UPDATE", data)
            
            elif message in ["PAGAMENTO_CONFIRMADO", "OPERACAO_CANCELADA", "FALHA_AUTENTICACAO"]:
                msg = bus_msg
                msg.token = 242424
                msg.data = formatted_response
                self.mbcontext.MB_ReplyMessage(msg, data=msg.data)
    
            elif message == "REQUISICAO_NUMERO_CARTAO":
                param = "CANCELA"
                return str(param)
    
            elif message in ["REQUISICAO_VALIDADE", "REQUISICAO_CODIGO_SEGURANÇA"]:
                formatted_response = formatted_response.split("\n")
                param = show_keyboard(pos_id, formatted_response[1], title=formatted_response[0], mask="INTEGER", numpad=True, buttons="$OK|$CANCEL")
                param = "CANCELA" if param is None else param
                return str(param)
    
            elif message == "REQUISICAO_ACAO":
                message_box = "Cancelar operação?"
                formatted_response = formatted_response.split("\n")
                param = show_messagebox(pos_id, message_box, title=formatted_response[0], buttons="$YES|$NO")
                if param == 0:
                    param = 1
                else:
                    param = 0
                return str(param)
    
            elif message == "REQUISICAO_DESCONECTAR_PINPAD":
                message_box = "Pinpad não encontrado. Por favor reconecte-o.\nTentar novamente?"
                param = show_messagebox(pos_id, message_box, title="", buttons="$YES|$NO")
                if param == 0:
                    param = 1
                else:
                    param = 0
                return str(param)
            elif message == "TRANSACAO_PENDENTE":
                message_box = "Última transação ainda pendente.\nDeseja confirmá-la?"
                param = show_messagebox(pos_id, message_box, title="", buttons="Confirmar|$CANCEL")
                if param == 0:
                    param = 1
                else:
                    param = 0
                return str(param)
        except BaseException as _:
            logger.exception("Error on callback")

    def _check_if_message_is_not_repeated(self, response):
        now = datetime.now()
        if response == self.last_response["message"] and (now - self.last_response["timestamp"]) < timedelta(seconds=3):
            return True
        else:
            self.last_response["message"] = response
            self.last_response["timestamp"] = now
            return False

    @staticmethod
    def _format_response(response):
        return _remove_accents(response)


def _remove_accents(text):
    if type(text) == str:
        return text
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
