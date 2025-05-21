from typing import Callable, Any
from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta
from threading import Lock, Thread


class CacheSource(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_new_object(self):
        raise NotImplementedError()


class CacheExpiration(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def is_expired(self):
        raise NotImplementedError()

    @abstractmethod
    def renew(self):
        raise NotImplementedError()


class CacheManager:
    def __init__(self, cache_expiration, cache_source=None, new_object_func=None, threaded=False):
        # type: (CacheExpiration, CacheSource, Callable[[], Any], bool) -> None
        self.cache_expiration = cache_expiration
        self.cache_source = cache_source
        self.new_object_func = new_object_func
        self.threaded = threaded

        self.retrieving_object = False
        self.cached_object = None
        self.renew_lock = Lock()

    def get_cached_object(self, new_object_func=None):
        if (not self.cache_expiration.is_expired() or self.retrieving_object) and self.cached_object is not None:
            return self.cached_object

        with self.renew_lock:
            if (not self.cache_expiration.is_expired() or self.retrieving_object) and self.cached_object is not None:
                return self.cached_object

            self.retrieving_object = True

            if self.threaded:
                renew_thread = Thread(target=self._renew_cache, args=new_object_func)
                renew_thread.daemon = True
                renew_thread.start()
            else:
                self._renew_cache(new_object_func)

            return self.cached_object

    def _renew_cache(self, new_object_func):
        try:
            if new_object_func is not None:
                self.cached_object = new_object_func()
            elif self.new_object_func is not None:
                self.cached_object = self.new_object_func()
            else:
                self.cached_object = self.cache_source.get_new_object()

            self.cache_expiration.renew()
        finally:
            self.retrieving_object = False


class PeriodBasedExpiration(CacheExpiration):
    def __init__(self, period_in_minutes):
        self.periodInMinutes = period_in_minutes
        self.expiration_date = datetime.now() - timedelta(days=1)

    def is_expired(self):
        return datetime.now() > self.expiration_date

    def renew(self):
        self.expiration_date = datetime.now() + timedelta(minutes=self.periodInMinutes)


class InfiniteExpiration(CacheExpiration):
    def __init__(self):
        super(CacheExpiration, self).__init__()

    def is_expired(self):
        return False

    def renew(self):
        pass
