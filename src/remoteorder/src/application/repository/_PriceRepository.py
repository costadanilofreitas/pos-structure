# -*- coding: utf-8 -*-

from memorycache import CacheManager, PeriodBasedExpiration
from msgbus import MBEasyContext
from persistence import Driver
from typing import Dict, Tuple


class PriceRepository(object):
    def __init__(self, mb_context):
        # type: (MBEasyContext) -> None
        self.mb_context = mb_context
        self._product_prices_cache = CacheManager(PeriodBasedExpiration(5), new_object_func=self._product_prices_cache_renovator)
        self._price_key_cache = CacheManager(PeriodBasedExpiration(5), new_object_func=self._price_key_cache_renovator)

    def get_all_price_keys(self):
        # type: () -> Dict[(unicode, unicode): unicode]
        return self._price_key_cache.get_cached_object()

    def get_all_prices(self):
        # type: () -> Dict[(unicode, unicode): Tuple[float, float, float]]
        return self._product_prices_cache.get_cached_object()

    def _product_prices_cache_renovator(self):
        # type: () -> Tuple[unicode, float, float]
        conn = None
        try:
            conn = Driver().open(self.mb_context)
            return {(x.get_entry(0).decode('utf-8'), x.get_entry(1).decode('utf-8'), x.get_entry(2).encode("utf-8") if x.get_entry(2) is not None else u""):  (
                float(x.get_entry(3)) if x.get_entry(3) is not None else 0.0,
                float(x.get_entry(4)) if x.get_entry(4) is not None else 0.0) for x in conn.select("""
                                        SELECT PriceListId, ProductCode, Context, DefaultUnitPrice, AddedUnitPrice
                                        FROM Price 
                                        WHERE ValidThru >= datetime(datetime(), 'localtime') AND ValidFrom <= datetime(datetime(), 'localtime') """)}
        finally:
            if conn:
                conn.close()

    def _price_key_cache_renovator(self):
        conn = None
        try:
            conn = Driver().open(self.mb_context)
            return {(x.get_entry(0).decode("utf-8"), str(x.get_entry(1)), str(x.get_entry(2) or '')): x.get_entry(3) for x in conn.select("""
                                            SELECT PriceListId, ProductCode, Context, PriceKey
                                            FROM productdb.Price
                                            WHERE ValidThru >= datetime(datetime(), 'localtime') AND ValidFrom <= datetime(datetime(), 'localtime') """)}
        finally:
            if conn:
                conn.close()
