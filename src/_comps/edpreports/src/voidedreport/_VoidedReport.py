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
         Relatorio Cancelamento - Data Fiscal
         Loja.........: 99999
         Data/hora....: 03/05/2018 12:12:22
         Data Fiscal..: 02/05/18 - 03/05/18
         ID Operador..: Todos (POS # 01)
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
        header += u" Relatorio Cancelamento - {0:>11}\n".format(report_type_text)
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
        value_voided_orders = 0.0
        orders_dates = {}
        voided_reasons = {}
        body_dict = {}

        try:
            locale.setlocale(locale.LC_ALL, "portuguese_brazil")
        except:
            locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

        for order in voided_orders:
            value_voided_orders += order.total

            order_date = int(datetime.strftime(order.datetime, "%Y%m%d"))
            order_time_int = int(datetime.strftime(order.datetime, "%H%M"))
            order_time = datetime.strftime(order.datetime, "%H:%M")
            order.authorizer = int(order.authorizer) if order.authorizer else u" ---- "

            if not order_date in orders_dates:
                orders_dates[order_date] = {}
                orders_dates[order_date]['qty'] = 1
                orders_dates[order_date]['value'] = order.total
            else:
                orders_dates[order_date]['qty'] += 1
                orders_dates[order_date]['value'] += order.total

            if order.reason not in voided_reasons:
                voided_reasons[order.reason] = {}
                voided_reasons[order.reason]['qty'] = 1
                voided_reasons[order.reason]['value'] = order.total
            else:
                voided_reasons[order.reason]['qty'] += 1
                voided_reasons[order.reason]['value'] += order.total

            reason_body = u"{0:>10} {1} {2:>6} {3:>6} {4:>7}\n".format(order.id, order_time, str(order.operator)[:6],
                                                                       str(order.authorizer)[:6],
                                                                       locale.format("%.2f", order.total, True))
            if order_date not in body_dict:
                body_dict[order_date] = {}
            if order.reason not in body_dict[order_date]:
                body_dict[order_date][order.reason] = {}
            if order_time_int not in body_dict[order_date][order.reason]:
                body_dict[order_date][order.reason][order_time_int] = reason_body
            else:
                body_dict[order_date][order.reason][order_time_int] += reason_body

        body = u"Descricao          Qtd    Total\n"
        body += u"Cancelamentos....: [{0:>4}] R${1:>10}\n" \
                u"Resumo...........:\n".format(qty_voided_orders, locale.format("%.2f", value_voided_orders, True))
        for reason_name, reason in voided_reasons.items():
            body += u" {0:.<16}: [{1:>4}] R${2:>10}\n".format(reason_name[:16], reason['qty'],
                                                             locale.format("%.2f", reason['value'], True))

        for date_int, date in sorted(body_dict.items()):
            date_str = str(date_int)
            date_text = date_str[6:8]+'/'+date_str[4:6]+'/'+date_str[0:4]
            body += u"--------------------------------------\n"
            body += u"    Pedido  Hora Operad Autori   Total\n"
            body += u"{0:>10}.......: [{1:>4}] R${2:>10}\n".format(date_text, orders_dates[date_int]['qty'],
                                                                   locale.format("%.2f", orders_dates[date_int]['value'], True))
            for reason_name, lines in sorted(date.items()):
                body += u"{0:.<17}: \n".format(reason_name[:17])
                for hour, line in sorted(lines.items()):
                    body += line

        body += u"======================================\n"

        return body
