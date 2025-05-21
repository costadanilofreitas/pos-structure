from application.domain.ui import InfoMessage
from sysactions import show_info_message


class MsgBusInfoMessage(InfoMessage):
    def __init__(self, pos_id):
        self.pos_id = pos_id

    def show(self, message, msg_type=None):
        show_info_message(self.pos_id, message, msgtype=msg_type.name)
