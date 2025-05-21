from abc import ABCMeta
from xml.etree import cElementTree as eTree

from dateutil import tz
from msgbus import TK_SYS_ACK, FM_PARAM, TK_HV_COMPLIST, MBEasyContext
from persistence import Connection, Driver
from sysactions import show_any_dialog, show_keyboard
from systools import sys_log_error
from typing import Callable, Any, List


class BaseRepository(object):
    __metaclass__ = ABCMeta

    def __init__(self, mbcontext):
        # type: (MBEasyContext) -> None
        self.mbcontext = mbcontext

    def execute_with_connection(self, method, db_name=None, service_name=None):
        # type: (Callable[[Connection], Any], int, str) -> Any
        conn = None
        try:
            conn = Driver().open(self.mbcontext,
                                 dbname=str(db_name) if db_name is not None else None,
                                 service_name=service_name)
            return method(conn)
        finally:
            if conn is not None:
                conn.close()

    def execute_with_transaction(self, method, db_name=None, service_name=None):
        # type: (Callable[[Connection], Any], int, str) -> Any
        def transaction_method(conn):
            # type: (Connection) -> Any

            conn.transaction_start()
            try:
                conn.query("BEGIN TRANSACTION")
                ret = method(conn)
                conn.query("COMMIT")
                return ret
            except:
                conn.query("ROLLBACK")
                raise
            finally:
                conn.transaction_end()

        return self.execute_with_connection(transaction_method, db_name=db_name, service_name=service_name)

    def execute_in_all_databases(self, method, pos_list):
        # type: (Callable[[Connection], Any], List[int]) -> Any
        ret = []
        for pos in pos_list:
            conn = None
            try:
                conn = Driver().open(self.mbcontext, dbname=str(pos))
                ret.append(method(conn))
            finally:
                if conn is not None:
                    conn.close()

        return ret

    def execute_in_all_databases_returning_flat_list(self, method, pos_list):
        # type: (Callable[[Connection], Any], List[int]) -> Any
        inner_ret = self.execute_in_all_databases(method, pos_list)

        ret = []
        for inner_list in inner_ret:
            ret.extend(inner_list)

        return ret


def show_message_dialog(pos_id, title="$INFORMATION", message="", mask="", assync=False):
    return show_any_dialog(pos_id, "messageDialog", message, title, "", "", "", 600000, mask, "", "", "", None, assync)


def show_message_options_dialog(pos_id, buttons, title="$INFORMATION", message=""):
    resp = show_any_dialog(
        pos_id, "messageOptionsDialog", message, title, "", buttons, "", 600000, "", "", "", "", None, False)

    if resp in (None, ''):
        return resp

    return int(resp)


def show_numpad_dialog(pos_id, title="", message="", mask="INTEGER"):
    resp = show_keyboard(pos_id, message, title=title, mask=mask, numpad=True)

    if resp in (None, '', 'NaN'):
        return resp

    return int(resp) if (mask != "CURRENCY" and mask != "NUMBER") else float(resp)


def show_filtered_list_box_dialog(pos_id, options, title="", message="", mask=""):
    if type(options) == list:
        options = "|".join(options)
    resp = show_any_dialog(
        pos_id, "filteredListBox", message, title, options, "", "",  600000, mask, "", "", "", None, False)

    if resp in (None, ''):
        return resp

    return int(resp)


def show_bordereau_dialog(pos_id):
    return show_any_dialog(
        pos_id, "bordereauDialog", '', "$BORDEREAU", "", "", "", 600000, "mask", "", "", "", None, False)


def show_confirm_dialog(pos_id, title=''):
    if not title:
        title = "$BORDEREAU"
    return show_any_dialog(
        pos_id, "bordereauDialog", 'confirmDialog', title, "", "", "", 600000, "mask", "", "", "", None, False)


def components_is_running(mb_context, *params):
    msg_resp = mb_context.MB_EasySendMessage("HyperVisor", TK_HV_COMPLIST, FM_PARAM)
    if msg_resp.token != TK_SYS_ACK:
        sys_log_error("Unable to obtain the TK_HV_COMPLIST")
        return False

    component_list = [_.get('name').lower() for _ in eTree.XML(msg_resp.data).findall(".//component[@status='1']")]
    for component in params:
        if component.lower() not in component_list:
            return False

    return True


def ensure_iterable(value):
    if isinstance(value, basestring):
        return [value]

    try:
        _ = (e for e in value)
        return value
    except TypeError:
        return [value]


def ensure_list(value):
    if isinstance(value, basestring):
        return [value]

    if isinstance(value, list):
        return value

    try:
        _ = (e for e in value)
        return list(value)
    except TypeError:
        return [value]


def convert_to_dict(iterable):
    ret = {}
    for item in iterable:
        ret[item] = item
    return ret


def convert_from_localtime_to_utc(localtime):
    # type: (datetime) -> datetime
    from_zone = tz.tzlocal()
    to_zone = tz.tzutc()
    localtime = localtime.replace(tzinfo=from_zone)
    utc = localtime.astimezone(to_zone)

    return utc
