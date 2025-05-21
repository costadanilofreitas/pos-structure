from model import BaseThread
from cfgtools import Group
from msgbus import MBEasyContext
from datetime import datetime
from time import sleep

from rupture_events import RuptureEvents, RuptureEventTypes


class CleanRuptureThread(BaseThread):

    def __init__(self, mb_context, configs):
        # type: (MBEasyContext, Group) -> None

        super(CleanRuptureThread, self).__init__()

        self._mb_context = mb_context

        self._start = configs.find_value("Rupture.CleanRuptureTimeWindow.StartTime", None)
        self._end = configs.find_value("Rupture.CleanRuptureTimeWindow.EndTime", None)
        self._interval = int(configs.find_value("Rupture.CleanRuptureTimeWindow.Interval", "30"))

    def run(self):
        while self.running:
            sleep_time = self._interval
            
            try:
                now = datetime.now().time().isoformat()
                should_run = self._start and self._end and self._start <= now <= self._end

                if should_run:
                    self._mb_context.MB_EasyEvtSend(
                        RuptureEvents.CleanRupture, RuptureEventTypes.CleanRuptureThread, ""
                    )

            finally:
                sleep(sleep_time)
