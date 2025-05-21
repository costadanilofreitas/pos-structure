import time
from logging import Logger

from threading import Lock, Thread, local
from ._MessageProcessorCallback import MessageProcessorCallback


class TimeProcessorCallback(MessageProcessorCallback):
    def __init__(self, logger, log_time):
        # type: (Logger, float) -> None
        self.logger = logger
        self.log_time = log_time

        self.count_lock = Lock()
        self.current_count = 0
        self.process_time = 0
        self.local_storage = local()

        t = Thread(target=self.print_result)
        t.daemon = True
        t.start()

    def process_begun(self, event_name, request_id, data):
        self.local_storage.start_time = time.process_time()

    def input_parsed(self, event_name, request_id, input_obj):
        pass

    def business_called(self, event_name, request_id, input_obj, output_obj):
        pass

    def process_finished(self, event_name, request_id, input_obj, output_obj):
        self.calculate_end()

    def parse_exception(self, event_name, request_id, data, exception):
        self.calculate_end()

    def unhandled_exception(self, event_name, request_id, input_obj, exception):
        self.calculate_end()

    def calculate_end(self):
        end = time.process_time()
        with self.count_lock:
            self.process_time += end - self.local_storage.start_time
            self.current_count += 1

    def print_result(self):
        while True:
            with self.count_lock:
                process_time = self.process_time
                current_count = self.current_count
                self.process_time = 0
                self.current_count = 0

            if current_count > 0:
                self.logger.info("Count: {}, Process average time: {} ms".format(
                    current_count,
                    int((process_time / current_count) * 1000)))

            time.sleep(self.log_time)
