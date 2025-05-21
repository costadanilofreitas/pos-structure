from logging import Logger

from mw_helper import ensure_iterable
from production.repository import ProductRepository
from typing import List, Optional, Union

from ._AddTagBox import AddTagBox
from ._ProductionBox import ProductionBox


class JitAddTagBox(AddTagBox):
    def __init__(self, name, sons, product_repository, tag, jit_lines, logger=None):
        # type: (str, Optional[Union[List[ProductionBox], ProductionBox]], ProductRepository, List[str], List[str], Logger) -> None # noqa
        part_codes = product_repository.get_part_codes_of_jit_lines(ensure_iterable(jit_lines))
        super(JitAddTagBox, self).__init__(name, sons, tag, part_codes, logger)
