from abc import ABCMeta, abstractmethod
from typing import Optional  # noqa


class ScreenActions(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def show_listbox(self, posid, options, message='$SELECT_AN_OPTION', title='', defvalue='', buttons='$OK|$CANCEL',
                     icon='', timeout=60000, asynch=False):
        # type: (str, List[str], Optional[str], Optional[str], Optional[str], Optional[str],  Optional[str], Optional[int], Optional[bool]) -> None
        raise NotImplementedError()
