from abc import ABCMeta, abstractmethod


class OperatorNameRetriever(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_operator_name(self, operator_id):
        # type: (int) -> str
        raise NotImplementedError()
