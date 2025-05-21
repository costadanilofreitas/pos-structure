from abc import ABCMeta, abstractmethod
from typing import Optional
from ._DefaultMessageProcessorExecutor import MessageProcessor
from ._ApiRequest import ApiRequest


class ApiRouter(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_message_processor(self, api_request):
        # type: (ApiRequest) -> Optional[MessageProcessor]
        raise NotImplementedError()
