from abc import ABCMeta, abstractmethod
from typing import Any  # noqa

from ._Report import Report  # noqa


class Presenter(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def present(self, dto):
        # type: (Any) -> Report
        raise NotImplementedError()
