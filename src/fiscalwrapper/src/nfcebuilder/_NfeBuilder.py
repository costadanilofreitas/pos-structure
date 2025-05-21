# -*- coding: utf-8 -*-

from typing import List, Dict, Any
from pos_model import Order
from old_helper import remove_xml_namespace
from _ContextKeys import ContextKeys

from _NfceXmlPartBuilder import NfceXmlPartBuilder
from nfceutil import NfeSigner


class NfeBuilder(NfceXmlPartBuilder):
    _nfce_template = """<NFe xmlns="http://www.portalfiscal.inf.br/nfe">{0}</NFe>"""

    def __init__(self, part_builders, xml_signer, inf_nfe_compl_builder):
        # type: (List[NfceXmlPartBuilder], NfeSigner, NfceXmlPartBuilder) -> None
        self.part_builders = part_builders
        self.xml_signer = xml_signer
        self.inf_nfe_compl_builder = inf_nfe_compl_builder

    def build_xml(self, order, context):
        # type: (Order, Dict[unicode, Any]) -> unicode

        inner_xml = ""
        for part_builder in self.part_builders:
            inner_xml += part_builder.build_xml(order, context)

        unsigned_nfe = self._nfce_template.format(inner_xml)

        signature = self.xml_signer.get_signature(unsigned_nfe)
        signature_xml = remove_xml_namespace(signature)
        context[ContextKeys.digest_value] = signature_xml.find(".//Reference/DigestValue").text

        inf_nfe_comp = self.inf_nfe_compl_builder.build_xml(order, context)

        inner_xml += inf_nfe_comp
        inner_xml += signature

        return self._nfce_template.format(inner_xml)
