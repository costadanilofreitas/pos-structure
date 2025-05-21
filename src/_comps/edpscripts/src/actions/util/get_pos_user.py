from xml.etree import cElementTree as eTree

from msgbus import TK_POS_LISTUSERS, FM_PARAM, TK_SYS_NAK
from sysactions import send_message


def get_pos_users(pos_id):
    msg = send_message("POS%d" % int(pos_id), TK_POS_LISTUSERS, FM_PARAM, "%s" % pos_id)
    if msg.token == TK_SYS_NAK:
        raise Exception("Fail listing operators")
    xml = eTree.XML(msg.data)
    return [tag for tag in xml.findall("User")]


def get_opened_pos_user(pos_id, user_id):
    pos_user = None
    user_list = get_pos_users(pos_id)
    user_filter = filter(lambda x: x.get("id") == str(user_id) and not x.get("closeTime"), user_list)
    if user_filter not in [None, [], ""]:
        pos_user = user_filter[0]
    return pos_user
