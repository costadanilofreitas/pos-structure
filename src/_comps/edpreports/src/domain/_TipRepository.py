from abc import ABCMeta, abstractmethod
from ._OperatorTip import OperatorTip


class TipRepository(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_tips_per_operator(self, start_date, end_date, operator):
        # type: (datetime, datetime, str) -> List[OperatorTip]
        raise NotImplementedError
