# -*- coding: utf-8 -*-
import types

from datetime import datetime, timedelta
from threading import Lock, Thread


class ICacheSource(object):
    def __init__(self):
        pass

    def get_new_object(self):
        raise NotImplementedError()


class ICacheExpiration(object):
    def __init__(self):
        pass

    def is_expired(self):
        raise NotImplementedError()

    def renew(self):
        raise NotImplementedError()


class CacheManager:
    def __init__(self, cache_expiration, cache_source=None, new_object_func=None, threaded=False):
        # type: (ICacheExpiration, ICacheSource, types.FunctionType, bool) -> None
        self.cache_expiration = cache_expiration
        self.cache_source = cache_source
        self.new_object_func = new_object_func
        self.threaded = threaded

        self.retrieving_object = False
        self.cached_object = None
        self.renew_lock = Lock()

    def get_cached_object(self, new_object_func=None):
        # Se o cache não expirou ou se já estamos buscando o novo objeto, retornamos o que está no cache
        if (not self.cache_expiration.is_expired() or self.retrieving_object) and self.cached_object is not None:
            return self.cached_object

        # O cache expirou, vamos renová-lo então adquirimos o lock
        with self.renew_lock:
            # Apos adquirir o lock, verificamos novamente pois pode ser que outra thread ja tenha atualizado
            if (not self.cache_expiration.is_expired() or self.retrieving_object) and self.cached_object is not None:
                return self.cached_object

            # Somos a primeira thread a adquirir o lock, vamos atualizar o dado a partir do arquivo
            self.retrieving_object = True

            # Se trabalhamos com thread, criamos uma thread para buscar o novo objeto e retornamos o objeto que esta no cache
            if self.threaded:
                renew_thread = Thread(target=self._renew_cache, args=new_object_func)
                renew_thread.start()
            else:
                self._renew_cache(new_object_func)

            return self.cached_object

    def _renew_cache(self, new_object_func):
        try:
            # Atualizamos o objeto seguinte a prioridade
            # 1 - função passada como parâmetro no método de renovação
            # 2 - função passada como parâmetro no construtor
            # 3 - objecto que implementa ICacheSource
            if new_object_func is not None:
                self.cached_object = new_object_func()
            elif self.new_object_func is not None:
                self.cached_object = self.new_object_func()
            else:
                self.cached_object = self.cache_source.get_new_object()

            self.cache_expiration.renew()
        finally:
            self.retrieving_object = False


class PeriodBasedExpiration(ICacheExpiration):
    def __init__(self, period_in_minutes):
        super(ICacheExpiration, self).__init__()
        self.periodInMinutes = period_in_minutes

        # Iniciamos o cache expirado
        self.expiration_date = datetime.now() - timedelta(days=1)

    def is_expired(self):
        return datetime.now() > self.expiration_date

    def renew(self):
        self.expiration_date = datetime.now() + timedelta(minutes=self.periodInMinutes)


class InfiniteExpiration(ICacheExpiration):
    def __init__(self):
        super(ICacheExpiration, self).__init__()

    def is_expired(self):
        return False

    def renew(self):
        pass
