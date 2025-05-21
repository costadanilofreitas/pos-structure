from abc import ABCMeta, abstractmethod


class PosController(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def open_user(self, user_id):
        # type: (str) -> None
        raise NotImplementedError()

    @abstractmethod
    def log_in_user(self, user_id):
        # type: (str) -> None
        raise NotImplementedError()

    @abstractmethod
    def log_out_user(self):
        # type: () -> None
        raise NotImplementedError()

    @abstractmethod
    def close_user(self, user_id):
        # type: (str) -> None
        raise NotImplementedError()

    @abstractmethod
    def set_pod_function(self, pos_function):
        # type: (str) -> None
        raise NotImplementedError()
