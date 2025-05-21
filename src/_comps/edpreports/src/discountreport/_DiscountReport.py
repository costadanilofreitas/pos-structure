# -*- coding: utf-8 -*-

import locale
from datetime import datetime

from typing import Optional

from repository import OrderRepository


class DiscountReport(object):
    TypeRealDate = "RealDate"
    TypeBusinessPeriod = "BusinessPeriod"
    TypeSessionId = "SessionId"

    def __init__(self, order_repository, store_id):
        # type: (OrderRepository, unicode) -> None
        self.order_repository = order_repository
        self.store_id = store_id

        try:
            locale.setlocale(locale.LC_ALL, "portuguese_brazil")
        except:
            locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

    def generate_discount_report_by_real_date(self, pos_id, report_pos, initial_date, end_date, operator_id):
        # type: (int, Optional[unicode], datetime, datetime, Optional[unicode]) -> str
        return self._generate_discount_report(self.TypeRealDate, pos_id, report_pos, initial_date, end_date, operator_id, None)

    def generate_discount_report_by_business_period(self, pos_id, report_pos, initial_date, end_date, operator_id):
        # type: (int, Optional[unicode], datetime, datetime, unicode) -> str
        return self._generate_discount_report(self.TypeBusinessPeriod, pos_id, report_pos, initial_date, end_date, operator_id, None)

    def generate_discount_report_by_session_id(self, pos_id, session_id):
        # type: (int, Optional[unicode]) -> str
        return self._generate_discount_report(self.TypeSessionId, pos_id, None, None, None, None, session_id)

    def _generate_discount_report(self, report_type, pos_id, report_pos, initial_date, end_date, operator_id, session_id):
        # type: (unicode, int, Optional[unicode], Optional[datetime], Optional[datetime], Optional[unicode], Optional[unicode]) -> str
        discount_orders = None
        if report_type == self.TypeRealDate:
            discount_orders = self.order_repository.get_discount_orders_by_real_date(initial_date, end_date, operator_id, report_pos)

        elif report_type == self.TypeBusinessPeriod:
            discount_orders = self.order_repository.get_discount_orders_by_business_period(initial_date, end_date, operator_id, report_pos)

        elif report_type == self.TypeSessionId:
            discount_orders = self.order_repository.get_discount_orders_by_session_id(session_id)
            start_index = session_id.find("user=")
            end_index = session_id.find(",", start_index)
            operator_id = session_id[start_index + 5:end_index]
            start_index = session_id.find("period=")
            initial_date = end_date = datetime.strptime(session_id[start_index + 7:], "%Y%m%d")

        header = self._build_header(report_type, pos_id, report_pos, initial_date, end_date, operator_id)
        body = self._build_body(discount_orders)

        report = header + body
        report_bytes = report.encode("utf-8")

        return report_bytes

    def _build_header(self, report_type, pos_id, report_pos, initial_date, end_date, operator_id):
        operator = "Todos"
        if operator_id is not None:
            operator = operator_id

        pos_list = "Todos" if report_pos is None else report_pos.zfill(2)
        if report_type == self.TypeRealDate:
            report_type_text = "Data Fiscal"
        elif report_type == self.TypeBusinessPeriod:
            report_type_text = "Dia Negocio"
        else:
            report_type_text = "Surpresa"
            pos_list = pos_id

        header =  u"======================================\n"
        header += u"  Relatorio Descontos - {0:>11}\n".format(report_type_text)
        header += u" Loja.........: " + self.store_id.zfill(5) + "\n"
        header += u" Data/hora....: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "\n"
        header += u" {0:.<13}: {1} - {2}\n".format(report_type_text, initial_date.strftime("%d/%m/%y"), end_date.strftime("%d/%m/%y"))
        header += u" ID Operador..: " + u"{0} (POS # {1})\n".format(operator, str(pos_id).zfill(2))
        temp_pos_list = u" POS incluidos: " + u"{0}".format(pos_list)
        header += temp_pos_list[:38]
        if len(temp_pos_list) > 38:
            header += (u"\n                %s" % temp_pos_list[38:60])
        if len(temp_pos_list) > 66:
            header += (u"\n                %s" % temp_pos_list[60:82])
        header += u"\n"

        return header

    @staticmethod
    def _build_body(discount_orders):
        discount_qty = len(discount_orders)
        total_discount_value = sum([order.discount_amount for order in discount_orders])

        body = u"======================================\n"
        body += u"    Descricao       Qtd      Total\n"
        body += u"Total Descontos..: [{0:>4}] R${1:>10}\n".format(discount_qty, _float_convert(total_discount_value))
        body += u"======================================\n"
        body += u"PEDIDOS".center(38)
        body += u"\n======================================\n"
        for order in discount_orders:
            body += "\nPed./Hora..: {0:>12} /   {1:>8}\n".format(str(order.order_id), _format_date(order.applied_date))
            body += "Total/Desc.:   R${0:>8} / R${1:>8}\n".format(_float_convert(order.total_gross),
                                                                  _float_convert(order.discount_amount))
            body += "Operator...: {0:>25}\n".format(order.operator[:20])
            body += "Autorizador: {0:>25}\n".format(order.authorizer[:20])
            body += u"--------------------------------------\n"

        return body


def _format_date(date):
    return datetime.strftime(date, "%H:%M:%S")


def _float_convert(value):
    return locale.format("%.2f", value, True)
