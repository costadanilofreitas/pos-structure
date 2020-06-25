from typing import List, Dict, Any
from pos_model import Order

from _SatXmlPartBuilder import SatXmlPartBuilder


class InfCfeBuilder(SatXmlPartBuilder):
    cnf_random = ""
    cdv = ""

    def __init__(self, part_builders):
        # type: (List(SatXmlPartBuilder)) -> None
        self.part_builders = part_builders

    def build_xml(self, order, context):
        # type: (Order, Dict[unicode, Any]) -> unicode
        inner_xml = ""
        for part_builder in self.part_builders:
            inner_xml += part_builder.build_xml(order, context)

        infcfe_xml = "<infCFe versaoDadosEnt='0.07'>"
        infcfe_xml += inner_xml
        infcfe_xml += "</infCFe>"

        return infcfe_xml
