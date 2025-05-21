from .. import Waiter
from messagebus import Event
from typing import List


class ResolvedWaiter(Waiter):
    def __init__(self, sync_id, events):
        # type: (str, List[Event]) -> None
        self.sync_id = sync_id
        self.events = events

    def get_sync_id(self):
        return self.sync_id

    def get_events(self):
        return self.events
