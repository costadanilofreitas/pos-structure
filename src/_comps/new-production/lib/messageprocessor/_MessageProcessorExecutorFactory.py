from abc import ABCMeta, abstractmethod

from ._MessageProcessor import MessageProcessor
from ._MessageProcessorExecutor import MessageProcessorExecutor


class MessageProcessorExecutorFactory(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def build_executor(self, message_processor):
        # type: (MessageProcessor) -> MessageProcessorExecutor
        raise NotImplementedError()
