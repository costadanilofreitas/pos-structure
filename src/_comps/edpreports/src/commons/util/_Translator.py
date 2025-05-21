from abc import ABCMeta, abstractmethod
from typing import List, Dict  # noqa


class Translator(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def translate_labels(self, labels, pos_id):
        # type: (List[str], int) -> Dict[str, str]
        raise NotImplementedError()
