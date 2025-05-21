from abc import ABCMeta, abstractmethod

from typing import List, Dict  # noqa


class L10n(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def localize(self, labels):
        # type: (List[str]) -> Dict[str, str]
        raise NotImplementedError()
