from abc import ABCMeta, abstractmethod


class MessageBox(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def show(self, pos_id, message, title='$INFORMATION', icon='info', buttons='$OK', timeout=60000, asynch=False,
             linefeed='\\', focus=True):
        #  type: (str, str, str, str, str, int, bool, str, bool) -> None
        raise NotImplementedError()
