from abc import ABCMeta, abstractmethod

from typing import List, Dict  # noqa


class I18n(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def internationalize(self, labels):
        # type: (List[str]) -> Dict[str, str]
        raise NotImplementedError()

    def internationalize_text(self, text):
        # type: (str) -> str
        raise NotImplementedError()
