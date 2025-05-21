# -*- coding: utf-8 -*-

from datetime import datetime

from repository import OrderRepository
from typing import List, Union
from voidedlinesreport.repository import UsersRepository

from .model import Line


class VoidedLinesReport(object):
    def __init__(self, order_repository, users_repository, store_id):
        # type: (OrderRepository, UsersRepository, str) -> None
        self.order_repository = order_repository
        self.users_repository = users_repository
        self.store_id = store_id

    def generate_voided_lines_report(self, report_pos, initial_date, end_date, only_body, operator_id):
        # type: (Union[str, None], datetime, datetime, bool, Union[int, None]) -> unicode
        voided_lines = self.get_voided_lines(report_pos, initial_date, end_date, operator_id)

        if only_body:
            return self._build_body(voided_lines).encode("utf-8") if len(voided_lines) > 0 else ""

        report = self._build_header(report_pos, initial_date, end_date)
        report += self._build_body(voided_lines) if len(voided_lines) > 0 else ""

        return report.encode("utf-8")

    def get_voided_lines(self, report_pos, initial_date, end_date, operator_id):
        # type: (Union[str, None], datetime, datetime, Union[int, None]) -> List[Line]
        voided_lines = self.order_repository.get_voided_lines(report_pos, initial_date, end_date, operator_id)
        self.users_repository.get_operators_name(voided_lines)
        return voided_lines

    def _build_header(self, report_pos, initial_date, end_date):
        # type: (Union[str, None], datetime, datetime) -> unicode
        """
        ======================================
           Relatorio de Linhas Canceladas
         Data/hora..: 26/08/2019 15:06:26
         Periodo....: 26/08/2019 - 26/08/2019
         POS(s).....: Todos
        ======================================
        """

        pos_list = "Todos" if report_pos is None else report_pos.zfill(2)

        header = u"======================================\n"
        header += u"   Relatorio de Linhas Canceladas\n"
        header += u" Loja.......: " + self.store_id.zfill(5) + "\n"
        header += u" Data/hora..: {}\n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        header += u" Periodo....: {} - {}\n".format(initial_date.strftime("%d/%m/%y"), end_date.strftime("%d/%m/%y"))
        header += u" POS(s).....: {}\n".format(pos_list)
        header += u"======================================\n"

        return header

    @staticmethod
    def _build_body(voided_lines):
        # type: (List[Line]) -> unicode
        """
        Operador            Qtd   Valor
             1 - 1          [  1] R$      10.9
          5813 - Desenvolve [  5] R$     77.74
        ======================================
        """
        operators_line = {}
        for line in voided_lines:
            if line.operator not in operators_line:
                operators_line[line.operator] = [line]
            else:
                operators_line[line.operator].append(line)

        body = u"Operador            Qtd   Valor\n"

        for operator in operators_line:
            operator_name = next(iter(operators_line[operator])).operator_name
            operator_qty_sum = 0
            operator_price_sum = 0.0
            for line in operators_line[operator]:
                operator_qty_sum += line.quantity
                operator_price_sum += line.price

            body += u"{0:>6} - {1:<10} [{2:>3}] R${3:>10}\n".format(str(operator)[:6],
                                                                    operator_name[:10],
                                                                    operator_qty_sum,
                                                                    operator_price_sum)

        body += u"======================================\n"
        return body
