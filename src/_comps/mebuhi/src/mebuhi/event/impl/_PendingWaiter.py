from threading import Condition

from .. import Waiter


class PendingWaiter(Waiter):
    def __init__(self, sync_id):
        # type: (str) -> None
        self.sync_id = sync_id
        self.event = None
        self.condition = Condition()

    def get_sync_id(self):
        return self.sync_id

    def get_events(self):
        with self.condition:
            if self.event is None:
                self.condition.wait()
        return [self.event]

    def new_event(self, event):
        with self.condition:
            self.event = event
            self.condition.notify()
