# -*- coding: utf-8 -*-

from application.repository import PriceRepository
from typing import List, Union, Tuple


class PriceService(object):
    def __init__(self, price_repository, price_list_order):
        # type: (PriceRepository, List[str]) -> None
        self.price_repository = price_repository
        self.price_list_order = price_list_order

    def get_best_price_key(self, item_id, part_code, price_lists=None):
        # type: (str, str, List[str]) -> Union[str, None]
        if price_lists is None:
            price_lists = self.price_list_order

        price_key_cache = self.price_repository.get_all_price_keys()
        return self._get_best_price_from_price_cache(item_id, part_code, price_lists, price_key_cache)

    def get_best_price(self, item_id, part_code, price_lists=None):
        # type: (unicode, unicode, bool) -> Union[Tuple[float, float], None]
        if price_lists is None:
            price_lists = self.price_list_order

        price_cache = self.price_repository.get_all_prices()
        return self._get_best_price_from_price_cache(item_id, part_code, price_lists, price_cache)

    @staticmethod
    def _get_best_price_from_price_cache(item_id, part_code, price_lists, price_cache):
        current_context = item_id
        while True:
            for price_list in price_lists:
                key = (price_list, part_code, current_context)
                if key in price_cache:
                    return price_cache[key]

            if current_context == "":
                return None

            index = current_context.find('.')
            if index < 0:
                current_context = ""
            else:
                current_context = current_context[index + 1:]
