# -*- coding: utf-8 -*-

from xml.etree import cElementTree as eTree

from msgbus import MBEasyContext, TK_POS_LISTUSERS, FM_PARAM, TK_SYS_ACK, TK_CMP_TERM_NOW
from mwhelper import BaseRepository
from persistence import Connection
from sysactions import get_model


class PosStateFixer(BaseRepository):
    def __init__(self, mb_context):
        # type: (MBEasyContext) -> None
        super(PosStateFixer, self).__init__(mb_context)
        self.mb_context = mb_context

    def fix_business_period(self, pos_id):
        # type: (str) -> None
        model = get_model(pos_id)
        operator = model.find("Operator")

        list_users_msg = self.mb_context.MB_EasySendMessage("POS%d" % int(pos_id), TK_POS_LISTUSERS, FM_PARAM, "%s" % pos_id, timeout=600000000)
        if list_users_msg.token != TK_SYS_ACK:
            raise Exception("Error retrieving user list. {0}: {1}".format(list_users_msg.token, list_users_msg.data))

        list_users_xml = eTree.XML(list_users_msg.data)
        opened_users = [tag for tag in list_users_xml.findall("User") if not tag.get("closeTime")]

        if operator is not None and operator.get("state") == "LOGGEDIN" and len(opened_users) == 0:
            self._fix_pos_sate(pos_id)

            comp_stop_msg = self.mb_context.MB_EasySendMessage("POS%d" % int(pos_id), TK_CMP_TERM_NOW, timeout=600000000)
            if comp_stop_msg.token != TK_CMP_TERM_NOW:
                raise Exception("Error stopping component. {0}: {1}".format(comp_stop_msg.token, comp_stop_msg.data))

        elif operator is None and len(opened_users) > 0:
            self._fix_opened_users(pos_id)

            comp_stop_msg = self.mb_context.MB_EasySendMessage("POS%d" % int(pos_id), TK_CMP_TERM_NOW, timeout=600000000)
            if comp_stop_msg.token != TK_CMP_TERM_NOW:
                raise Exception("Error stopping component. {0}: {1}".format(comp_stop_msg.token, comp_stop_msg.data))

    def _fix_pos_sate(self, pos_id):
        # type: (str) -> None
        def inner_func(conn):
            # type: (Connection) -> None
            conn.query(self._fix_pos_state_query.format(pos_id))

        self.execute_with_connection(inner_func)

    _fix_pos_state_query = """UPDATE PosState SET BusinessPeriod = (SELECT MAX(BusinessPeriod) FROM UserCount WHERE POSId = '{0}' AND CloseTime is NULL) WHERE POSId = '{0}' """

    def _fix_opened_users(self, pos_id):
        # type: (str) -> None
        def inner_func(conn):
            # type: (Connection) -> None
            conn.query(self._fix_opened_users_query.format(pos_id))

        self.execute_with_connection(inner_func)

    _fix_opened_users_query = """UPDATE UserCount SET CloseTime = (SELECT MAX(OpenTime) FROM UserCount WHERE POSId = '{0}') WHERE POSId = '{0}' AND CloseTime is NULL"""
