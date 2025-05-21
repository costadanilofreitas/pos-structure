from abc import ABCMeta, abstractmethod

from typing import List


class ReportBuilder(object):

    @abstractmethod
    def generate(self):
        # type: () -> List
        raise NotImplementedError()