from abc import ABCMeta, abstractmethod


class OrderPictureRepository(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_order_picture(self, order_id):
        # type: (int) -> str
        raise NotImplementedError()
