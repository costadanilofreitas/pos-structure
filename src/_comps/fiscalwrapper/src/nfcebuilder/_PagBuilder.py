# -*- coding: utf-8 -*-

import logging

from old_helper import validar_cnpj
from pos_model import Order, TenderType, XmlTenderType, XmlTenderTypeFromPOSMapper

from _NfceXmlPartBuilder import NfceXmlPartBuilder
from typing import Dict, Any

logger = logging.getLogger("FiscalWrapper")


class PagBuilder(NfceXmlPartBuilder):

    def __init__(self, versao_ws):
        # type: (int) -> None
        self.versao_ws = versao_ws

    def build_xml(self, order, context):
        # type: (Order, Dict[unicode, Any]) -> unicode

        if self.versao_ws not in (1, 3):
            xml = "<pag>"
        else:
            xml = ""
        for tender in order.tenders:
            tipo = XmlTenderTypeFromPOSMapper.get(tender.type)

            cnpj = validar_cnpj(tender.cnpj_auth)

            if tender.type in [TenderType.credit, TenderType.debit] and cnpj is False:
                tipo = XmlTenderType.others

            if self.versao_ws not in (1, 3):
                xml += "<detPag>"
            else:
                xml += "<pag>"

            if self.versao_ws in (1, 3):
                total_amount = tender.amount - tender.change
            else:
                total_amount = tender.amount

            xml += "<tPag>{:>02}</tPag><vPag>{:>0.2f}</vPag>".format(tipo, total_amount)

            if tipo in [XmlTenderType.credit, XmlTenderType.debit] and cnpj is not False:

                bandeira = '99'
                xml += "<card><tpIntegra>1</tpIntegra><CNPJ>{0}</CNPJ><tBand>{1}</tBand><cAut>{2}</cAut></card>"\
                    .format(tender.cnpj_auth.strip(), bandeira.strip(), tender.auth_code.strip())

            if self.versao_ws not in (1, 3):
                xml += "</detPag>"
            else:
                xml += "</pag>"

            if self.versao_ws not in (1, 3) and tender.change > 0.0:
                xml += "<vTroco>{:>0.2f}</vTroco>".format(tender.change)

        if self.versao_ws not in (1, 3):
            xml += "</pag>"
        return xml
