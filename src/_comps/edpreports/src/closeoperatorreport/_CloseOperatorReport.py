# encoding: utf-8

import datetime
import json
import time
from cStringIO import StringIO
from xml.etree import cElementTree as eTree

from sysactions import get_user_information

from model import TransferType
from old_helper import convert_from_utf_to_localtime
from utils import center, join, double_line_separator, add_amount_line, empty_line, add_table_line, add_key_value_line

DATE_TIME_FMT = "%d/%m/%Y %H:%M:%S"


class CloseOperatorReport(object):
    def __init__(self, order_repository, product_repository, account_repository, store_id):
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.account_repository = account_repository
        self.store_id = store_id

    def generate_close_operator_report(self, pos_id, operator_id, period, session_id, cash_report, authorizer):
        report = StringIO()
        report.write(self._close_operator_report_header(int(pos_id), operator_id, period, authorizer))
        self._close_operator_report_body(report, session_id, cash_report)

        return report.getvalue()

    def _close_operator_report_header(self, pos_id, operator_id, period, authorizer):
        title = center("Logout Operador")
        current_datetime = time.strftime(DATE_TIME_FMT)
        formatted_store_id = self.store_id.zfill(5) + "\n"
        fiscal_date = "%02d/%02d/%04d" % (int(period[6:8]), int(period[4:6]), int(period[:4]))
        separator = double_line_separator()
        authorizer_text = "Autorizador...: %(authorizer)s" if authorizer is not None else ""
        operator_name = eTree.XML(get_user_information(operator_id)).find(".//user").get("LongName")[:15]

        return ("""
%(separator)s
%(title)s
Loja.........: %(formatted_store_id)s
Data/hora....: %(current_datetime)s
Data fiscal..: %(fiscal_date)s
Operador.....: %(operator_name)s (POS # %(pos_id)02d)
%(authorizer_text)s
%(separator)s""" % join(globals(), locals()))

    def _close_operator_report_body(self, report, session_id, cash_report):
        paid_orders_by_tender_type = self.order_repository.get_paid_orders_by_tender_type(session_id)
        tenders_description = self.product_repository.get_tenders_descripton()
        transfers = self.account_repository.get_all_transfers(session_id)
        declared_amounts = [transfer for transfer in transfers
                            if transfer.account_type == TransferType.DECLARED_AMOUNT.value]

        report.write(center("RESUMOS"))
        report.write(cash_report)
        self._write_cash_in_and_cash_out(transfers, declared_amounts, paid_orders_by_tender_type, report)
        report.write(double_line_separator())
        self._write_declared_amounts(declared_amounts, paid_orders_by_tender_type, tenders_description, report)

    @staticmethod
    def _write_cash_in_and_cash_out(transfers, declared_amounts, paid_orders_by_tender_type, report):
        initial_transfer = [transfer for transfer in transfers
                            if transfer.account_type == TransferType.INITIAL_AMOUNT.value]
        initial_transfer = 0.0 if len(initial_transfer) == 0 else initial_transfer[0].amount
        all_cash_in = [transfer for transfer in transfers
                       if transfer.account_type == TransferType.TRANSFER_CASH_IN.value]
        all_cash_out = [transfer for transfer in transfers
                        if transfer.account_type == TransferType.TRANSFER_CASH_OUT.value]
        total_cash = sum(order.amount if order.tender_id == '0' else 0 for order in paid_orders_by_tender_type)
        total_cash_in = sum(cash.amount for cash in all_cash_in)
        total_cash_out = sum(cash.amount for cash in all_cash_out)

        report.write(center("SUPRIMENTOS/SANGRIAS"))
        report.write(add_amount_line("Fundo Inicial", None, initial_transfer))

        all_cash_in_and_out = [transfer for transfer in transfers
                               if transfer.account_type in (TransferType.TRANSFER_CASH_IN.value,
                                                            TransferType.TRANSFER_CASH_OUT.value)]
        for cash in all_cash_in_and_out:
            cash_type = "Suprimento {}h" if cash.account_type == TransferType.TRANSFER_CASH_IN.value \
                                         else "Sangria    {}h"
            date = datetime.datetime.strptime(cash.operation_date, "%Y-%m-%d %H:%M:%S")
            date = convert_from_utf_to_localtime(date)
            hour = str(date.hour) + ":" + str(date.minute)
            report.write(add_amount_line(cash_type.format(hour), None, cash.amount))

        drawer_amount = total_cash + total_cash_in - total_cash_out
        declared_cash_amount = [transfer for transfer in declared_amounts if transfer.tender_id == 0]
        declared_cash_amount = 0.0 if len(declared_cash_amount) == 0 else declared_cash_amount[0].amount
        report.write(add_amount_line("Gaveta", None, drawer_amount))
        report.write(add_amount_line("Declarado", None, declared_cash_amount))
        report.write(add_amount_line("Diferenca", None, drawer_amount - declared_cash_amount))

    @staticmethod
    def _write_declared_amounts(declared_amounts, paid_orders_by_tender_type, tenders_description, report):
        report.write(center("BORDEREAU"))
        header = ["Pagamento", "Declarado", "Diferenca"]
        columns_height = [18, 10, 10]
        align = ['left', 'right', 'right']
        format_type = ['string', 'float', 'float']
        character_to_add = [".:", " ", " "]
        report.write(add_table_line(header, columns_height, align))
        total_in = 0
        total_declared = 0
        glaccount = ''
        for declared in declared_amounts:
            if declared.tender_id == 0:
                glaccount = declared.glaccount

            sold_amount = sum(order.amount if order.tender_id == str(declared.tender_id) else 0
                              for order in paid_orders_by_tender_type)

            total_in += sold_amount
            total_declared += declared.amount

            line = [tenders_description[str(declared.tender_id)], declared.amount, sold_amount - declared.amount]
            report.write(add_table_line(line, columns_height, align, format_type, character_to_add))
        report.write(empty_line())
        glaccount = "" if not glaccount else json.loads(glaccount)
        if glaccount:
            report.write(add_amount_line("Diferenca total", None, total_in - total_declared))
            report.write(add_key_value_line("Numero Envelope..: ", glaccount["envelope"]))
            report.write(add_key_value_line("Justificativa....: ", glaccount["justification"]))
