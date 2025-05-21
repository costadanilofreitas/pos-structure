import datetime
from Queue import Queue, Empty
from logging import Logger
from threading import Thread

from production.command import ProductionCommand
from typing import Any


class UniqueQueue(Queue):
    def _put(self, item):
        for i in self.queue:
            if hash(i) == hash(item):
                return
        self.queue.append(item)


class CommandQueue(object):
    def __init__(self, production_manager, logger):
        # type: (Any, Logger) -> None
        self.production_manager = production_manager
        self.logger = logger
        self.command_queue = UniqueQueue()
        self.running = True

        self.processor_thread = Thread(target=self.consume_queue)
        self.processor_thread.daemon = True
        self.processor_thread.start()

    def put(self, command):
        # type: (ProductionCommand) -> None
        self.logger.info("Command putted on queue: {}".format(type(command)))
        self.command_queue.put(command)

    def consume_queue(self):
        while self.running:
            command_type = None
            try:
                self.logger.info("Command queue size: {}".format(self.command_queue.qsize()))
                command = self.command_queue.get(True, 5)
                start_time = datetime.datetime.now()
                command_type = type(command)

                self.logger.info("Starting to process command: {}".format(command_type))
                self.production_manager.process_command(command)
                end_time = datetime.datetime.now()
                time_delta = (end_time - start_time).total_seconds()
                self.logger.info("Process command time: {} - {}".format(time_delta, command_type))
            except Empty:
                continue
            except BaseException as _: # noqa
                self.logger.exception("Error processing command: {}".format(command_type))

    def stop(self):
        self.running = False
