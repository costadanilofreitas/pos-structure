# -*- coding: utf-8 -*-
import sysactions
import logging
import msgbus
import pyscripts
import bustoken
import os
import time

from threading import Thread
from inspect import getmembers
from xml.etree import cElementTree as eTree
from old_helper import config_logger

mbcontext = pyscripts.mbcontext
config_logger(os.environ["LOADERCFG"], 'TimeActions')
logger = logging.getLogger("TimeActions")

msg_token_dict = getmembers(msgbus)
msg_token_dict.extend(getmembers(bustoken))

msg_bus_send_message = msgbus.MBEasyContext.MB_EasySendMessage
show_any_dialog = sysactions.show_any_dialog
update_any_dialog = sysactions.update_any_dialog
show_info_message = sysactions.show_info_message
set_custom = sysactions.set_custom


def get_token_name(token):
    for func_name, func_value in msg_token_dict:
        if token == func_value:
            return func_name


def _action_received(params):
    xml, subject, evt_type = params[:3]
    logger.debug("### START ### - ### {} ###".format(evt_type))

    fn = sysactions._actions.get(evt_type)
    try:
        if fn:
            args = [el.findtext('.').encode('UTF-8') for el in eTree.XML(xml).findall('Param')]
            return fn(*args)
        else:
            return None
    finally:
        logger.debug("### ENDED ### - ### {} ###\n".format(evt_type))


def MB_EasySendMessage(self, dest_name, token, format=0, data=None, timeout=-1):
    token_name = get_token_name(token)
    if token == msgbus.TK_CMP_MESSAGE:
        token_name = token_name + '.{}'.format(data.split('\0')[0])

    try:
        logger.debug("### SEND  ### - {}.{}".format(dest_name, token_name))

        if token == msgbus.TK_PRN_PRINT:
            print_thread = Thread(target=_printer_retry, args=(self, data, dest_name, format, timeout, token))
            print_thread.daemon = True
            print_thread.start()
            ret = msgbus.MBHttpMessage(msgbus.TK_SYS_ACK, None, None)
        else:
            ret = msg_bus_send_message(self, dest_name, token, format, data, timeout)
        return ret

    finally:
        logger.debug("### RECV  ### - {}.{}".format(dest_name, token_name))


def _printer_retry(self, data, dest_name, print_format, timeout, token):
    retry = 0
    while retry < 5:
        try:
            ret = msg_bus_send_message(self, dest_name, token, print_format, data, timeout)
            if ret.token == msgbus.TK_SYS_ACK:
                logger.info("[_printer_retry] Success printing received data")
                break
        except msgbus.MBException as _:
            logger.error("[_printer_retry] Error printing received data")

        time.sleep(0.75)
        retry += 1
        logger.error("[_printer_retry] Retry number: {}".format(retry))
    return


def _encode_utf8(text):
    if text and isinstance(text, unicode):
        text = text.encode("utf-8")
    return text


def custom_show_any_dialog(*args, **kwargs):
    args = [_encode_utf8(x) for x in args]
    kwargs = {key: _encode_utf8(value) for key, value in kwargs.items()}
    return show_any_dialog(*args, **kwargs)


def custom_update_any_dialog(*args, **kwargs):
    args = [_encode_utf8(x) for x in args]
    kwargs = {key: _encode_utf8(value) for key, value in kwargs.items()}
    return update_any_dialog(*args, **kwargs)


def custom_show_info_message(*args, **kwargs):
    args = [_encode_utf8(x) for x in args]
    kwargs = {key: _encode_utf8(value) for key, value in kwargs.items()}
    return show_info_message(*args, **kwargs)


def custom_set_custom(*args, **kwargs):
    args = [_encode_utf8(x) for x in args]
    kwargs = {key: _encode_utf8(value) for key, value in kwargs.items()}
    return set_custom(*args, **kwargs)


def main():
    msgbus.MBEasyContext.MB_EasySendMessage = MB_EasySendMessage
    pyscripts.unsubscribe_event_listener('POS_ACTION', sysactions._action_received)
    pyscripts.subscribe_event_listener('POS_ACTION', _action_received)

    sysactions.show_any_dialog = custom_show_any_dialog
    sysactions.update_any_dialog = custom_update_any_dialog
    sysactions.show_info_message = custom_show_info_message
    sysactions.set_custom = custom_set_custom
