from typing import List, Dict, Any
from pos_model import Order

from _SatXmlPartBuilder import SatXmlPartBuilder


class CfeBuilder(SatXmlPartBuilder):
    _cfe_template = """<?xml version='1.0' encoding='UTF-8'?><CFe>{0}</CFe>"""

    def __init__(self, part_builders):
        # type: (List[SatXmlPartBuilder]) -> None
        self.part_builders = part_builders

    def build_xml(self, order, context):
        # type: (Order, Dict[unicode, Any]) -> unicode

        inner_xml = ""
        for part_builder in self.part_builders:
            inner_xml += part_builder.build_xml(order, context)

        return self._cfe_template.format(inner_xml)
