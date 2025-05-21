from typing import Dict, Any
from pos_model import Order
from _NfceXmlPartBuilder import NfceXmlPartBuilder


class EmitBuilder(NfceXmlPartBuilder):
    def __init__(self,
                 crt,
                 cnpj_contribuinte,
                 inscr_estadual,
                 nome_emit,
                 end_logradouro,
                 end_numero,
                 end_compl,
                 bairro,
                 c_mun_fg,
                 municipio,
                 uf,
                 cep):
        # type: (int, unicode, unicode, unicode, unicode, unicode, unicode, unicode, unicode, unicode, unicode, unicode) -> None

        self.crt = crt
        self.cnpj_contribuinte = cnpj_contribuinte
        self.nome_emit = nome_emit
        self.end_logradouro = end_logradouro
        self.end_numero = end_numero
        self.end_compl = end_compl
        self.bairro = bairro
        self.c_mun_fg = c_mun_fg
        self.uf = uf
        self.cep = cep
        self.inscr_estadual = inscr_estadual
        self.municipio = municipio

    def build_xml(self, order, context):
        # type: (Order, Dict[unicode, Any]) -> unicode

        # Dados Emitente
        # CRT: 1 = simples nacional, 2 = simples (excesso de sublimite de recieta), 3 = regime normal
        inner_xml = "<emit>" \
                    "<CNPJ>%s</CNPJ>" \
                    "<xNome>%s</xNome>" \
                    "<enderEmit>" \
                    "<xLgr>%s</xLgr>" \
                    "<nro>%s</nro>" % (self.cnpj_contribuinte, self.nome_emit, self.end_logradouro, self.end_numero)

        if self.end_compl:
            inner_xml += "<xCpl>%s</xCpl>" % self.end_compl

        inner_xml += "<xBairro>%s</xBairro>" \
               "<cMun>%s</cMun>" \
               "<xMun>%s</xMun>" \
               "<UF>%s</UF>" \
               "<CEP>%s</CEP>" \
               "</enderEmit>" \
               "<IE>%s</IE>" \
               "<CRT>%d</CRT>" \
               "</emit>" % (self.bairro, self.c_mun_fg, self.municipio, self.uf, self.cep, self.inscr_estadual, self.crt)

        return inner_xml
