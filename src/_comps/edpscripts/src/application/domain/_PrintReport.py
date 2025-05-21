from abc import ABCMeta, abstractmethod

from typing import List  # noqa


class PrintReport(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def send_print(self, pos_id, preview, report_name, *report_params):
        # type: (str, bool, str, List[any]) -> str
        raise NotImplementedError()
