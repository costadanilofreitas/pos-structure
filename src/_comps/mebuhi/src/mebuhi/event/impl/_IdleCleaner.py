from threading import Thread, Condition

from .._Cleaner import Cleaner


class IdleCleaner(object):
    def __init__(self, cleaner, interval, logger):
        # type: (Cleaner, float, Logger) -> None
        self.cleaner = cleaner
        self.interval = interval
        self.running = False
        self.thread = None
        self.logger = logger
        self.sleep_condition = Condition()

    def start(self):
        self.running = True
        self.thread = Thread(name="IdleCleaner", target=self._clean_runner)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.running = False
        with self.sleep_condition:
            self.sleep_condition.notify()

    def _clean_runner(self):
        while self.running:
            try:
                self.cleaner.clean_idle_listeners()
                with self.sleep_condition:
                    self.sleep_condition.wait(self.interval)
            except BaseException as _: # noqa
                self.logger.exception("Error into clean runner")


