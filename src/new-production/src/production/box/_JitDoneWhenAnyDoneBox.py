from logging import Logger

from mw_helper import ensure_iterable
from production.repository import ProductRepository
from typing import List, Optional, Union

from ._DoneWhenAnyDoneBox import DoneWhenAnyDoneBox
from ._ProductionBox import ProductionBox


class JitDoneWhenAnyDoneBox(DoneWhenAnyDoneBox):
    def __init__(self, name, sons, product_repository, jit_lines, logger=None):
        # type: (str, Optional[Union[List[ProductionBox]], ProductionBox], ProductRepository, List[str], Logger) -> None
        jit_lines = ensure_iterable(jit_lines)

        part_codes = product_repository.get_part_codes_of_jit_lines(jit_lines)
        super(JitDoneWhenAnyDoneBox, self).__init__(name, sons, part_codes, logger)
