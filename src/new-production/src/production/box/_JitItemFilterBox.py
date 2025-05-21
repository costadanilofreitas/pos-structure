from logging import Logger

from mw_helper import ensure_iterable
from production.box import ProductionBox
from production.repository import ProductRepository
from typing import List, Optional, Union

from ._ItemFilterBox import ItemFilterBox


class JitItemFilterBox(ItemFilterBox):
    def __init__(self, name, sons, product_repository, allowed_jits, forbidden_jits, show_all_items, logger=None):
        # type: (str, Optional[Union[List[ProductionBox]], ProductionBox], ProductRepository, Union[str, List[str]], Union[str, List[str]], unicode, Logger) -> None # noqa
        allowed_part_codes = None
        forbidden_part_codes = None

        if allowed_jits is not None:
            allowed_jits = ensure_iterable(allowed_jits)
            allowed_part_codes = product_repository.get_part_codes_of_jit_lines(allowed_jits)

        if forbidden_jits is not None:
            forbidden_jits = ensure_iterable(forbidden_jits)
            forbidden_part_codes = product_repository.get_part_codes_of_jit_lines(forbidden_jits)

        super_class = super(JitItemFilterBox, self)
        super_class.__init__(name, sons, allowed_part_codes, forbidden_part_codes, show_all_items, logger)
