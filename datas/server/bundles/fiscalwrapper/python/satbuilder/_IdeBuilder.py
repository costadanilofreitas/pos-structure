from typing import Dict, Any
from datetime import datetime
from pos_model import Order
from dateutil import tz

from _SatXmlPartBuilder import SatXmlPartBuilder
from _ContextKeys import ContextKeys


class IdeBuilder(SatXmlPartBuilder):

    def __init__(self,
                 cnpj_sw, sign_ac):
        #  type: (unicode, unicode) -> None
        self.cnpj_sw = cnpj_sw
        self.sign_ac = sign_ac

    def build_xml(self, order, context):
        # type: (Order, Dict[unicode, Any]) -> unicode

        last_totaled_state = None
        for order_state in reversed(order.states):
            if order_state.name == "TOTALED":
                last_totaled_state = order_state
                break

        if last_totaled_state is None:
            raise Exception("The order was not totaled")

        data_emissao = self._format_date(last_totaled_state.timestamp)

        context[ContextKeys.data_emissao] = data_emissao

        inner_xml = "<ide>"\
                    "<CNPJ>%s</CNPJ>"\
                    "<signAC>%s</signAC>"\
                    "<numeroCaixa>%03d</numeroCaixa>"\
                    "</ide>" % (self.cnpj_sw, self.sign_ac, int(order.pos_id))
        return inner_xml

    @staticmethod
    def _format_date(data):
        # type: (datetime) -> str
        local_zone = tz.tzlocal()
        data = data.replace(tzinfo=local_zone)
        data_str = data.strftime("%Y-%m-%dT%H:%M:%S%z")
        data_str = data_str[:22] + ":" + data_str[22:]
        return data_str
