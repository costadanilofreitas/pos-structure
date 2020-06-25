from typing import Dict, Any
from pos_model import Order
from _SatXmlPartBuilder import SatXmlPartBuilder


class EmitBuilder(SatXmlPartBuilder):
    def __init__(self,
                 cnpj_contribuinte,
                 inscr_estadual):
        # type: (unicode, unicode) -> None

        self.cnpj_contribuinte = cnpj_contribuinte
        self.inscr_estadual = inscr_estadual

    def build_xml(self, order, context):
        # type: (Order, Dict[unicode, Any]) -> unicode

        # Dados Emitente
        inner_xml = "<emit>"\
                    "<CNPJ>%s</CNPJ>"\
                    "<IE>%s</IE>"\
                    "<cRegTribISSQN>1</cRegTribISSQN>"\
                    "<indRatISSQN>N</indRatISSQN>"\
                    "</emit>" % (self.cnpj_contribuinte, self.inscr_estadual)
        return inner_xml
