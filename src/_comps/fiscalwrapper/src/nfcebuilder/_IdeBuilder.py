from typing import Dict, Any
from datetime import datetime
from pos_model import Order
from dateutil import tz

from _NfceXmlPartBuilder import NfceXmlPartBuilder
from _ContextKeys import ContextKeys


class NfceEmissionType(object):
    normal = 1
    contingency = 9


class IdeBuilder(NfceXmlPartBuilder):

    def __init__(self,
                 serie,
                 initial_order_id,
                 c_uf,
                 mod,
                 c_mun_fg,
                 ambiente, versao_ws):
        #  type: (int, int, int, int, int, int, int) -> None
        self.serie = serie
        self.initial_order_id = initial_order_id
        self.c_uf = c_uf
        self.mod = mod
        self.c_mun_fg = c_mun_fg
        self.ambiente = ambiente
        self.chave = None
        self.versao_ws = versao_ws

    def build_xml(self, order, context):
        # type: (Order, Dict[unicode, Any]) -> unicode
        is_in_contingency = context[ContextKeys.is_in_contingency]
        contingency_datetime = context[ContextKeys.contingency_datetime]
        contingency_reason = context[ContextKeys.contingency_reason]

        last_totaled_state = None
        for order_state in reversed(order.states):
            if order_state.name == "TOTALED":
                last_totaled_state = order_state
                break

        if last_totaled_state is None:
            raise Exception("The order was not totaled")

        data_emissao = self._format_date(last_totaled_state.timestamp)

        context[ContextKeys.data_emissao] = data_emissao
        serie_nota = int(self.serie)

        numero_nota = self.initial_order_id + order.order_id
        context[ContextKeys.fiscal_number] = numero_nota

        tp_emis = NfceEmissionType.contingency if is_in_contingency else NfceEmissionType.normal
        context[ContextKeys.emission_type] = tp_emis

        inner_xml = "<ide>" \
                    "<cUF>%s</cUF>" \
                    "<cNF>${CNF_RANDOM}</cNF>" \
                    "<natOp>venda</natOp>" % self.c_uf
        if self.versao_ws in (1, 3):
            inner_xml += "<indPag>0</indPag>"
        inner_xml += "<mod>%s</mod>" \
                     "<serie>%s</serie>" \
                     "<nNF>%s</nNF>" \
                     "<dhEmi>%s</dhEmi>" \
                     "<tpNF>1</tpNF>" \
                     "<idDest>1</idDest>" \
                     "<cMunFG>%s</cMunFG>" \
                     "<tpImp>4</tpImp>" \
                     "<tpEmis>%d</tpEmis>" \
                     "<cDV>${CDV}</cDV>" \
                     "<tpAmb>%s</tpAmb>" \
                     "<finNFe>1</finNFe>" \
                     "<indFinal>1</indFinal>" \
                     "<indPres>1</indPres>" \
                     "<procEmi>0</procEmi>" \
                     "<verProc>v1.00.00</verProc>" \
                     % (self.mod,
                        serie_nota,
                        numero_nota,
                        data_emissao,
                        self.c_mun_fg,
                        tp_emis,
                        self.ambiente)

        if is_in_contingency:
            inner_xml += "<dhCont>{}</dhCont><xJust>{}</xJust>".format(
                self._format_date(contingency_datetime),
                contingency_reason)

        inner_xml += "</ide>"

        return inner_xml

    @staticmethod
    def _format_date(data):
        # type: (datetime) -> str
        local_zone = tz.tzlocal()
        data = data.replace(tzinfo=local_zone)
        data_str = data.strftime("%Y-%m-%dT%H:%M:%S%z")
        data_str = data_str[:22] + ":" + data_str[22:]
        return data_str
