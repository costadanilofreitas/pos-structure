from abc import ABCMeta, abstractmethod

from typing import List, Optional  # noqa


class ListBox(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def show_listbox(self, pos_id, options, message='$SELECT_AN_OPTION', title='', def_value='',
                     buttons='$OK|$CANCEL', icon='', timeout=60000, asynch=False):
        # type: (str, List[str], Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], Optional[int], Optional[bool]) -> int
        raise NotImplementedError()
