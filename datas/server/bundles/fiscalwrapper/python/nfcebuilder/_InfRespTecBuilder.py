from _ContextKeys import ContextKeys
from _NfceXmlPartBuilder import NfceXmlPartBuilder
from models import SoftwareDeveloper
from pos_model import Order
from typing import Dict, Any


class InfRespTecBuilder(NfceXmlPartBuilder):

    def __init__(self, software_deloveper):
        # type: (SoftwareDeveloper) -> None
        self.software_deloveper = software_deloveper # type: SoftwareDeveloper

    def build_xml(self, order, context):
        # type: (Order, Dict[unicode, Any]) -> unicode

        xml = ""

        if self.software_deloveper.enabled is True:
            xml += "<infRespTec>"

            xml += "<CNPJ>{}</CNPJ>".format(self.software_deloveper.cnpj)
            xml += "<xContato>{}</xContato>".format(self.software_deloveper.contact)
            xml += "<email>{}</email>".format(self.software_deloveper.email)
            xml += "<fone>{}</fone>".format(self.software_deloveper.phone)

            if self.software_deloveper.id_csrt and self.software_deloveper.csrt:
                xml += "<idCSRT>{}</idCSRT>".format(self.software_deloveper.id_csrt)
                xml += "<hashCSRT>${HASH_CSRT}</hashCSRT>"

                context[ContextKeys.csrt] = self.software_deloveper.csrt
                context[ContextKeys.id_csrt] = self.software_deloveper.id_csrt

            xml += "</infRespTec>"

        return xml
