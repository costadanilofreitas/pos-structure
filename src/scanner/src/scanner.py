import logging
import persistence
from messagehandler import EventHandler
from msgbus import MBEasyContext, FM_STRING
from bustoken import TK_PICKUPDISPLAY_ADD_READY_TO_PICK_ORDER
from threading import Thread

logger = logging.getLogger("scanner")


class Scanner(Thread):
    def __init__(self, mbcontext, com_port, baud_rate):
        try:
            super(Scanner, self).__init__()
            self.mbcontext = mbcontext
            self.com_port = com_port
            self.baud_rate = baud_rate
        except Exception as e:
            logger.info('[Scanner] Exception __init__ {}'.format(e))

    def _get_serial_component(self):
        try:
            import serial
            ret = serial.Serial(self.com_port, self.baud_rate, timeout=1.0)
            return ret
        except Exception as ex:
            logger.info('[Scanner] Exception get_serial_component {}'.format(ex))
            return None

    def run(self):
        conn_serial = self._get_serial_component()
        if conn_serial is not None:
            while True:
                try:
                    get_order_id = conn_serial.read(12) or ''
                    # logger.info('[Scanner] QRCde = {}'.format(get_order_id))
                    if len(get_order_id) == 12:
                        if get_order_id[:2] == 'QR' and get_order_id[-2:] == "BK":
                            order_id = get_order_id[2:10]
                            logger.info('[Scanner] reading loop: {}, TK_PICKUPDISPLAY_ADD_READY_TO_PICK_ORDER: {}'.format(order_id, TK_PICKUPDISPLAY_ADD_READY_TO_PICK_ORDER))
                            if int(order_id):
                                self.mbcontext.MB_EasySendMessage("PickupDisplay", TK_PICKUPDISPLAY_ADD_READY_TO_PICK_ORDER, format=FM_STRING, data=order_id.lstrip('0'), timeout=500000)
                except Exception as ex:
                    logger.exception('[Scanner] read loop failed, Ex: {0}'.format(ex))


class ScannerEventHandler(EventHandler):
    def __init__(self, mbcontext, scanner_uploader):
        super(ScannerEventHandler, self).__init__(mbcontext)
        self.mbcontext = mbcontext
        self.scanner = scanner_uploader

    def get_handled_tokens(self):
        return []

    def handle_message(self, msg):
        pass

    def handle_event(self, subject, type, data, msg):
        pass

    def terminate_event(self):
        Thread.join(self.scanner)
