import math
from datetime import timedelta

from timeutil import Clock


class OrderWithError(object):
    def __init__(self, order_id, clock):
        # type: (int, Clock) -> None
        self.order_id = order_id
        self.clock = clock

        self.retry_count = 0
        self.next_retry = clock.utc_now() + timedelta(seconds=10)
        self.enabled = True
        
    def update_retry_count(self):
        self.retry_count += 1
        if self.retry_count > 10:
            self.enabled = False
        else:
            self.next_retry = \
                self.next_retry + timedelta(seconds=math.pow(2, self.retry_count) * 10)
