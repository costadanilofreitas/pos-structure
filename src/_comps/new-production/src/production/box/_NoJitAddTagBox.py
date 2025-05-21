from logging import Logger

from production.repository import ProductRepository
from typing import List, Optional, Union

from ._AddTagBox import AddTagBox
from ._ProductionBox import ProductionBox


class NoJitAddTagBox(AddTagBox):
    def __init__(self, name, sons, product_repository, tag, logger=None):
        # type: (str, Optional[Union[List[ProductionBox], ProductionBox]], ProductRepository, List[str], Logger) -> None
        part_codes = product_repository.get_no_jit_part_codes()
        super(NoJitAddTagBox, self).__init__(name, sons, tag, part_codes, logger)
