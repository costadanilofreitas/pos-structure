import logging

import bustoken
from messagehandler import EventHandler
from msgbus import MBEasyContext, MBMessage, TK_SYS_ACK, TK_SYS_NAK
from typing import Optional

from fingerprintreader import DigitalPersonaFingerPrintReader, DigitalPersonaFingerPrintException

logger = logging.getLogger("FingerPrintReader")


class FingerPrintReaderEventHandler(EventHandler):
    def __init__(self, mbcontext, finger_print_reader):
        # type: (MBEasyContext, DigitalPersonaFingerPrintReader) -> None
        super(FingerPrintReaderEventHandler, self).__init__(mbcontext)

        self.finger_print_reader = finger_print_reader
        self.token_dictionary = {
            bustoken.TK_FPR_ENROLL_USER: self._handle_enroll_user,
            bustoken.TK_FPR_IDENTIFY_USER: self._handle_identify_user,
            bustoken.TK_FPR_AUTHORIZE_USER: self._handle_authorize_user,
            bustoken.TK_FPR_OK: self._handle_service_ok,
            bustoken.TK_FPR_RE_ENROLL_USER: self._handle_re_enroll_user
        }

    def get_handled_tokens(self):
        return self.token_dictionary.keys()

    def handle_message(self, msg):
        # type: (MBMessage) -> None
        event_handler = self.token_dictionary[msg.token]
        event_handler(self.mbcontext, msg)

    def handle_event(self, subject, evt_type, data, msg):
        raise NotImplementedError()

    def terminate_event(self):
        pass

    def _handle_identify_user(self, mbcontext, msg, authorization=False):
        # type: (MBEasyContext, MBMessage, Optional[bool]) -> None
        try:
            pos_id = msg.data
            finger_print_user_id = self.finger_print_reader.authenticate(pos_id, authorization)
            msg.token = TK_SYS_ACK
            logger.info("Successfully authentication for POS: #{}".format(pos_id))
            mbcontext.MB_ReplyMessage(msg, data=finger_print_user_id)
        except DigitalPersonaFingerPrintException as ex:
            data = None
            if ex.error_code == -2: # Timeout
                msg.token = bustoken.TK_FPR_TIMEOUT
            else:
                msg.token = TK_SYS_NAK
                data = str(ex.error_code) + " " + ex.message
                logger.error(data)

            mbcontext.MB_ReplyMessage(msg, data=data)
        except Exception as e:
            msg.token = TK_SYS_NAK
            data = e.message
            logger.exception(data)
            mbcontext.MB_ReplyMessage(msg, data=data)

    def _handle_authorize_user(self, mbcontext, msg):
        # type: (MBEasyContext, MBMessage) -> None
        try:
            self._handle_identify_user(mbcontext, msg, True)
        except Exception as _:
            logger.exception("[_handle_authorize_user]")

    def _handle_enroll_user(self, mbcontext, msg):
        # type: (MBEasyContext, MBMessage) -> None
        try:
            self._handle_enroll_and_re_enroll_user(mbcontext, msg, False)
        except Exception as _:
            logger.exception("[_handle_enroll_user]")

    def _handle_re_enroll_user(self, mbcontext, msg):
        # type: (MBEasyContext, MBMessage) -> None
        try:
            self._handle_enroll_and_re_enroll_user(mbcontext, msg, True)
        except Exception as _:
            logger.exception("[_handle_re_enroll_user]")

    def _handle_enroll_and_re_enroll_user(self, mbcontext, msg, replace):
        # type: (MBEasyContext, MBMessage, Optional[bool]) -> None
        user_id, pos_id = msg.data.split(";")
        if user_id is None:
            msg.token = TK_SYS_NAK
            data = "No user_id received"
            logger.info(data)
            mbcontext.MB_ReplyMessage(msg, data=data)
            return

        try:
            fmd_data = self.finger_print_reader.enroll_user(user_id, pos_id, replace)
            msg.token = TK_SYS_ACK
            mbcontext.MB_ReplyMessage(msg, data=fmd_data)
        except DigitalPersonaFingerPrintException as ex:
            msg.token = TK_SYS_NAK
            data = str(ex.error_code) + " " + ex.message

            if ex.error_code < 0:
                if ex.error_code == -1:
                    msg.token = bustoken.TK_FPR_FINGER_PRINT_ALREADY_REGISTERED
                    data = "Impressao digital ja cadastrada"
                    logger.error(data)

            mbcontext.MB_ReplyMessage(msg, data=data)
        except Exception as e:
            msg.token = TK_SYS_NAK
            data = e.message
            logger.exception(data)
            mbcontext.MB_ReplyMessage(msg, data=data)

    def _handle_service_ok(self, mbcontext, msg):
        # type: (MBEasyContext, MBMessage) -> None
        data = None
        try:
            self.finger_print_reader.check_device()
            logger.info("Device is found")
            msg.token = TK_SYS_ACK
        except Exception as e:
            logger.exception("Device is not found")
            data = e.message
            msg.token = TK_SYS_NAK

        mbcontext.MB_ReplyMessage(msg, data=data)


class FingerPrintReaderCallback:
    def __init__(self, mbcontext):
        # type: (MBEasyContext) -> None
        self.mbcontext = mbcontext

    def finger_print_reader_callback(self, event, pos_id, extra_data=""):
        # type: (str, str, Optional[str]) -> None
        data = pos_id
        if extra_data:
            data = pos_id + ";" + str(extra_data)

        logger.info("Callback: {}".format(data))
        self.mbcontext.MB_EasyEvtSend("FPR_CALLBACK", event, data)
