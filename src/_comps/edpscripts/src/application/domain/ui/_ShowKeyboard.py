from abc import ABCMeta, abstractmethod
from datetime import datetime  # noqa
from typing import Optional  # noqa


class ShowKeyboard(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def show(self, pos_id, message, title='$INPUT_DATA',
             buttons='$OK|$CANCEL', icon='info', timeout=60000, mask='', is_password=False,
             def_value='', min_value='', maxvalue='', num_pad=False, no_pad=False, no_input=False,
             asynch=False):
        # type: (str, str, Optional[str], Optional[str], Optional[str], Optional[str], Optional[int], Optional[str], Optional[bool], Optional[str], Optional[str], Optional[str], Optional[bool], Optional[bool], Optional[bool], Optional[bool]) -> str
        raise NotImplementedError()

    @abstractmethod
    def show_date(self, pos_id, message, title="", show_message_wrong_input_date=False):
        # type: (str, str, Optional[str], Optional[bool]) -> datetime
        raise NotImplementedError()
