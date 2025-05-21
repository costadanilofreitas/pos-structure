from typing import Dict, Any
from pos_model import Order

from old_helper import validar_cnpj, validar_cpf

from _NfceXmlPartBuilder import NfceXmlPartBuilder
from _ContextKeys import ContextKeys


class DestinatarioBuilder(NfceXmlPartBuilder):

    def __init__(self, ambiente):
        # type: (unicode) -> None
        self.ambiente = ambiente

    def build_xml(self, order, context):
        # type: (Order, Dict[unicode, Any]) -> unicode
        # Dados Destinatario (cliente)
        xml = ""
        cpf_cnpj = order.customer_cpf
        context[ContextKeys.cpf_cnpj] = cpf_cnpj

        if cpf_cnpj:
            xml += "<dest>"
            if len(cpf_cnpj) == 11 and validar_cpf(cpf_cnpj):
                xml += "<CPF>{}</CPF>".format(cpf_cnpj)
            elif len(cpf_cnpj) == 14 and validar_cnpj(cpf_cnpj):
                xml += "<CNPJ>{}</CNPJ>".format(cpf_cnpj)

            if self.ambiente == "2":
                xml += "<xNome>NF-E EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL</xNome>"

            xml += "<indIEDest>9</indIEDest>"
            xml += "</dest>"

        return xml
