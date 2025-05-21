from ._MessageProcessorExecutorFactory import MessageProcessorExecutorFactory
from ._DefaultMessageProcessorExecutor import DefaultMessageProcessorExecutor
from ._MessageProcessorCallback import MessageProcessorCallback


class DefaultMessageProcessorExecutorFactory(MessageProcessorExecutorFactory):
    def __init__(self, callbacks):
        # type: (List[MessageProcessorCallback]) -> None
        self.callbacks = callbacks

    def build_executor(self, message_processor):
        return DefaultMessageProcessorExecutor(message_processor, self.callbacks)
