from threading import Thread, Condition

from sysactions import set_custom

from msgbusboundary import MsgBusTableService as tableService
from actions.pos import pos_must_be_blocked


class UpdatePosBlockedState(Thread):
    def __init__(self, pos_list):
        super(UpdatePosBlockedState, self).__init__()
        self.pos_list = pos_list
        self.daemon = True
        self.thread_condition = Condition()

    def run(self):
        for pos_id in self.pos_list:
            set_custom(pos_id, 'POS_MUST_BE_BLOCKED', False)

        while True:
            for pos_id in self.pos_list:
                if pos_must_be_blocked(pos_id):
                    there_are_opened_tables = False
                    for table in tableService().list_tables(pos_id):
                        if int(table.status) != 1:
                            there_are_opened_tables = True
                            break
                    if not there_are_opened_tables:
                        set_custom(pos_id, 'POS_MUST_BE_BLOCKED', True)

            with self.thread_condition:
                self.thread_condition.wait(5 * 60)
