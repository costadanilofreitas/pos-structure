import time

from ._Sleeper import Sleeper


class RealSleeper(Sleeper):
    def sleep(self, secs):
        time.sleep(secs)
