from abc import ABCMeta, abstractmethod


class MessageProcessorExecutor(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute_processor(self, message_bus, message, event, data):
        raise NotImplementedError()
