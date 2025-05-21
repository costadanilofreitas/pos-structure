import collections
from datetime import datetime
from threading import Lock
from uuid import uuid4

from .. import Waiter

from ._PendingWaiter import PendingWaiter
from ._ResolvedWaiter import ResolvedWaiter


class Subscriber:
    def __init__(self):
        self.queue = collections.deque()
        self.last_seen = datetime.now()
        self.sync_id = str(uuid4())
        self.waiter_lock = Lock()
        self.pending_waiter = None  # type: PendingWaiter

    def new_event(self, event):
        with self.waiter_lock:
            if self.pending_waiter is not None:
                self.pending_waiter.new_event(event)
                self.pending_waiter = None
                self.last_seen = datetime.now()
            else:
                self.queue.append(event)

    def get_waiter(self):
        # type: () -> Waiter
        self.sync_id = str(uuid4())

        events = []
        with self.waiter_lock:
            if len(self.queue) > 0:
                try:
                    while True:
                        events.append(self.queue.popleft())
                except IndexError:
                    pass
            else:
                self.pending_waiter = PendingWaiter(self.sync_id)

        if len(events) > 0:
            return ResolvedWaiter(self.sync_id, events)
        else:
            return self.pending_waiter
