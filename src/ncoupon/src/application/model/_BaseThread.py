from threading import Thread, Condition


class BaseThread(Thread):
    def __init__(self):
        # type: () -> None

        super(BaseThread, self).__init__()
        self.running = True
        self.daemon = True
        self.sleep_condition = Condition()

    def stop(self):
        # type: () -> None

        self.running = False
        with self.sleep_condition:
            self.sleep_condition.notify_all()

    def sleep(self, time):
        # type: (int) -> None

        with self.sleep_condition:
            self.sleep_condition.wait(time)

    def wake_up(self):
        # type: () -> None

        with self.sleep_condition:
            self.sleep_condition.notify_all()
