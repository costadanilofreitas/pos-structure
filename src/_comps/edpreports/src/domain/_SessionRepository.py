from abc import ABCMeta, abstractmethod

from datetime import datetime  # noqa


class SessionRepository(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_unique_user_session_count(self, initial_date, end_date):
        # type: (datetime, datetime) -> int
        raise NotImplementedError()
