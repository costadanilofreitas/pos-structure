from pos_model import Order, XmlTenderTypeFromPOSMapper

from _SatXmlPartBuilder import SatXmlPartBuilder
from satbuilder import ContextKeys


class CfePagType(object):
    dinheiro = 1
    credito = 3
    debito = 4
    outros = 99


class PgtoBuilder(SatXmlPartBuilder):
    def build_xml(self, order, context):
        # type: (Order, ContextKeys) -> unicode

        xml = "<pgto>"
        # Pagamentos
        for tender in order.tenders:
            tipo = XmlTenderTypeFromPOSMapper.get(tender.type)


            xml += "<MP><cMP>{0:>02}</cMP><vMP>{1:>0.2f}</vMP><cAdmC>999</cAdmC></MP>".format(tipo, tender.amount)

        xml += "</pgto>"

        return xml
