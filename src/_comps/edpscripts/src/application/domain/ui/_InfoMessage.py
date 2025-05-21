from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Optional  # noqa


class InfoMessage(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def show(self, message, msg_type=None):
        # type: (str, Optional[InfoMessage.Type]) -> None
        raise NotImplementedError()

    class Type(Enum):
        info = 1
        warn = 2
        error = 3
