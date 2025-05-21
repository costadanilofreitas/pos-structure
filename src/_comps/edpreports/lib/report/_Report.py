from abc import ABCMeta, abstractmethod

from typing import List  # noqa

from ._Part import Part


class Report(object):
    __metaclass__ = ABCMeta

    key = "6910d546-252f-4b28-bc20-fae0aa8a2806"

    @abstractmethod
    def get_parts(self):
        # type: () -> List[Part]
        raise NotImplementedError()

    def get_width(self):
        # type: () -> int
        return 40
