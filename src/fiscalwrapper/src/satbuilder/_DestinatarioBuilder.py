from typing import Dict, Any
from pos_model import Order

from old_helper import validar_cnpj, validar_cpf

from _SatXmlPartBuilder import SatXmlPartBuilder
from _ContextKeys import ContextKeys


class DestinatarioBuilder(SatXmlPartBuilder):
    def build_xml(self, order, context):
        # type: (Order, Dict[unicode, Any]) -> unicode

        # Dados Destinatario (cliente)
        xml = ""
        cpf_cnpj = order.customer_cpf
        context[ContextKeys.cpf_cnpj] = cpf_cnpj

        if not cpf_cnpj:
            xml += "<dest/>"
        else:
            xml += "<dest>"
            if len(cpf_cnpj) == 11 and validar_cpf(cpf_cnpj):
                xml += "<CPF>{}</CPF>".format(cpf_cnpj)
            elif len(cpf_cnpj) == 14 and validar_cnpj(cpf_cnpj):
                xml += "<CNPJ>{}</CNPJ>".format(cpf_cnpj)

            xml += "</dest>"

        return xml
