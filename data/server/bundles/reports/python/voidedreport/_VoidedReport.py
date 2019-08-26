import locale
from datetime import datetime

from typing import List, Optional

from repository import OrderRepository
from .model import Order


class VoidedReport(object):
    TypeRealDate = "RealDate"
    TypeBusinessPeriod = "BusinessPeriod"
    TypeSessionId = "SessionId"

    def __init__(self, order_repository, store_id):
        # type: (OrderRepository, unicode) -> None
        self.order_repository = order_repository
        self.store_id = store_id

    def generate_voided_report_by_real_date(self, pos_id, report_pos, initial_date, end_date, operator_id):
        # type: (int, Optional[unicode], datetime, datetime, Optional[unicode]) -> str
        return self._generate_voided_report(self.TypeRealDate, pos_id, report_pos, initial_date, end_date, operator_id, None)

    def generate_voided_report_by_business_period(self, pos_id, report_pos, initial_date, end_date, operator_id):
        # type: (int, Optional[unicode], datetime, datetime, unicode) -> str
        return self._generate_voided_report(self.TypeBusinessPeriod, pos_id, report_pos, initial_date, end_date, operator_id, None)

    def generate_voided_report_by_session_id(self, pos_id, session_id):
        # type: (int, Optional[unicode]) -> str
        return self._generate_voided_report(self.TypeSessionId, pos_id, None, None, None, None, session_id)

    def _generate_voided_report(self, report_type, pos_id, report_pos, initial_date, end_date, operator_id, session_id):
        # type: (unicode, int, Optional[unicode], Optional[datetime], Optional[datetime], Optional[unicode], Optional[unicode]) -> str

        voided_orders = None
        if report_type == self.TypeRealDate:
            voided_orders = self.order_repository.get_voided_orders_by_real_date(initial_date, end_date, operator_id, report_pos)

        elif report_type == self.TypeBusinessPeriod:
            voided_orders = self.order_repository.get_voided_orders_by_business_period(initial_date, end_date, operator_id, report_pos)

        elif report_type == self.TypeSessionId:
            voided_orders = self.order_repository.get_voided_orders_by_session_id(session_id)
            start_index = session_id.find("user=")
            end_index = session_id.find(",", start_index)
            operator_id = session_id[start_index + 5:end_index]
            start_index = session_id.find("period=")
            initial_date = end_date = datetime.strptime(session_id[start_index + 7:], "%Y%m%d")

        count_pos_error = filter(lambda x:x == "error", voided_orders)
        count_pos_error = len(count_pos_error)

        voided_orders = filter(lambda x: x != "error", voided_orders)

        header = self._build_header(report_type, pos_id, report_pos, initial_date, end_date, operator_id, count_pos_error)
        body = self._build_body(voided_orders)

        report = header + body
        report_bytes = report.encode("utf-8")

        return report_bytes

    def _build_header(self, report_type, pos_id, report_pos, initial_date, end_date, operator_id, count_pos_error=0):
        # type: (unicode, int, Optional[unicode], datetime, datetime, unicode) -> unicode
        """
        ======================================
         Relatorio Cancelamentos - Data Fiscal
         Loja.........: 99999
         Data/hora....: 03/05/2018 12:12:22
         Data Fiscal..: 02/05/18 - 03/05/18
         ID Operador..: Todos (Reg # 01)
         POS incluido.: Todos
        ======================================"""
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
        header += u" Relatorio Cancelamentos - {0:>11}\n".format(report_type_text)
        header += u" Loja.........: " + self.store_id.zfill(5) + "\n"
        header += u" Data/hora....: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "\n"
        header += u" {0:.<13}: {1} - {2}\n".format(report_type_text, initial_date.strftime("%d/%m/%y"), end_date.strftime("%d/%m/%y"))
        header += u" ID Operador..: " + u"{0} (Reg # {1})\n".format(operator, str(pos_id).zfill(2))
        header += u" POS incluido.: " + u"{0}\n".format(pos_list)
        if count_pos_error > 0:
            header += u" POS excluidos: " + u"{0}\n".format(count_pos_error)
        header += u"======================================\n"

        return header

    @staticmethod
    def _build_body(voided_orders):
        """
        Descricao          Qtd    Total
        Cancelamentos....: [  14] R$    309,70
        --------------------------------------
            Pedido  Hora Operad Autori   Total
        18/05/2018.......: [  14] R$    309,70
        Mudou de Ideia...: [   5] R$    115,50
                11 16:07 123456   5813   23,90
        Pedido Salvo Canc: [   3] R$     52,80
                10 16:13 123456  ----     0,00
                12 16:13 123456      1   23,90
        Cancelamento.....: [   2] R$     45,80
                 4 13:46      1      1   21,90
        Pagamento Cancela: [   1] R$     23,90
                14 16:14 123456 123456   23,90
        ======================================
        :param voided_orders: the list of voided orders
        :return: the report bytes encoded with UTF-8
        """
        # type: (List[Order]) -> unicode

        qty_voided_orders = len(voided_orders)
        voided_orders = sorted(voided_orders, key=lambda x: x.datetime)
        value_voided_orders = 0.0
        orders_dates = {}
        date_qty = 0
        date_value = 0
        voided_reasons = {}
        voided_qty = 0
        voided_value = 0
        for order in voided_orders:
            value_voided_orders += order.total

            order_date = datetime.strftime(order.datetime, "%d/%m/%Y")
            if not order_date in orders_dates:
                orders_dates[order_date] = {}
                date_qty = 1
                date_value = order.total
            else:
                date_qty += 1
                date_value += order.total
            orders_dates[order_date]['qty'] = date_qty
            orders_dates[order_date]['value'] = date_value

            if order.reason not in voided_reasons:
                voided_reasons[order.reason] = {}
                voided_qty = 1
                voided_value = order.total
            else:
                voided_qty += 1
                voided_value += order.total
            voided_reasons[order.reason]['qty'] = voided_qty
            voided_reasons[order.reason]['value'] = voided_value

        try:
            locale.setlocale(locale.LC_ALL, "portuguese_brazil")
        except:
            locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

        body_dict = {}
        for order in voided_orders:
            order_date = datetime.strftime(order.datetime, "%d/%m/%Y")
            order_time = datetime.strftime(order.datetime, "%H:%M")
            order.authorizer = int(order.authorizer) if order.authorizer else u" ---- "
            reason_body = u"{0:>10} {1} {2:>6} {3:>6} {4:>7}\n".format(order.id, order_time, str(order.operator)[:6], str(order.authorizer)[:6], locale.format("%.2f", order.total, True))
            if order_date not in body_dict:
                body_dict[order_date] = {}
            if order.reason not in body_dict[order_date]:
                body_dict[order_date][order.reason] = reason_body
            else:
                body_dict[order_date][order.reason] += reason_body

        body = u"Descricao          Qtd    Total\n"
        body += u"Cancelamentos....: [{0:>4}] R${1:>10}\n".format(qty_voided_orders, locale.format("%.2f", value_voided_orders, True))
        for date in body_dict:
            body += u"--------------------------------------\n"
            body += u"    Pedido  Hora Operad Autori   Total\n"
            body += u"{0:>10}.......: [{1:>4}] R${2:>10}\n".format(date, orders_dates[date]['qty'], locale.format("%.2f", orders_dates[date]['value'], True))
            for reason in body_dict[date]:
                body += u"{0:.<17}: [{1:>4}] R${2:>10}\n".format(reason[:17], voided_reasons[reason]['qty'], locale.format("%.2f", voided_reasons[reason]['value'], True))
                body += body_dict[date][reason]

        body += u"======================================\n"

        return body
