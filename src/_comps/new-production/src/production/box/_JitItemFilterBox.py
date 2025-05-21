from logging import Logger

from mw_helper import ensure_iterable
from production.box import ProductionBox
from production.repository import ProductRepository
from typing import List, Optional, Union

from ._ItemFilterBox import ItemFilterBox


class JitItemFilterBox(ItemFilterBox):
    def __init__(self, name, sons, product_repository, allowed_jit_lines, excluded_jit_lines, forbidden_jit_lines,
                 show_all_items, logger=None):
        # type: (str, Optional[Union[List[ProductionBox]], ProductionBox], ProductRepository, Union[str, List[str]], Union[str, List[str]], Union[str, List[str]], unicode, Logger) -> None # noqa
        allowed_part_codes = None
        forbidden_part_codes = None
        excluded_part_codes = None

        if allowed_jit_lines is not None:
            allowed_jit_lines = ensure_iterable(allowed_jit_lines)
            allowed_part_codes = product_repository.get_part_codes_of_jit_lines(allowed_jit_lines)
        if excluded_jit_lines is not None:
            excluded_jit_lines = ensure_iterable(excluded_jit_lines)
            excluded_part_codes = product_repository.get_part_codes_of_jit_lines(excluded_jit_lines)
        if forbidden_jit_lines is not None:
            forbidden_jit_lines = ensure_iterable(forbidden_jit_lines)
            forbidden_part_codes = product_repository.get_part_codes_of_jit_lines(forbidden_jit_lines)

        super(JitItemFilterBox, self).__init__(name, sons, allowed_part_codes, excluded_part_codes,
                                               forbidden_part_codes, show_all_items, logger)
