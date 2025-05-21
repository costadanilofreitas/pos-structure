from abc import ABCMeta, abstractmethod

from _ScreenIdEnum import ScreenIdEnum  # noqa


class ScreenChanger(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def change(self, pos_id, screen_id_enum):
        # type: (str, ScreenIdEnum) -> None
        raise NotImplementedError()

    @abstractmethod
    def change_to_screen_name(self, pos_id, screen_name):
        # type: (str, str) -> None
        raise NotImplementedError()
