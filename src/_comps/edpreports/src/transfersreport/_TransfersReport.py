# encoding: utf-8
import json
import datetime
import time
from cStringIO import StringIO

from utils import add_amount_line, add_key_value_line, break_line, report_default_header, empty_line
from domain import TransferType
from old_helper import convert_from_utf_to_localtime

DATE_TIME_FMT = "%d/%m/%Y %H:%M:%S"


class TransfersReport(object):
    def __init__(self, account_repository, store_id):
        self.account_repository = account_repository
        self.store_id = store_id

    def generate_transfers_report(self, pos_id, operator_id, transfer_type, amount, period, envelope_number,
                                  print_operator_copy):
        print_operator_copy = print_operator_copy.lower() == 'true'
        report = StringIO()
        title = "Sangria" if int(transfer_type) == TransferType.TRANSFER_CASH_OUT.value else "Suprimento"
        title += " (Via Gerente)" if not print_operator_copy else " (Via Operador)"
        current_datetime = time.strftime(DATE_TIME_FMT)

        report.write(report_default_header(title, int(pos_id), operator_id, period, current_datetime))
        self._transfers_report_body(amount, envelope_number, "", report)

        return report.getvalue()

    def generate_transfers_report_by_period(self, pos_id, operator_id, transfer_type, period):
        transfer_type = int(transfer_type)
        transfers = self.account_repository.get_transfers_by_period(period, transfer_type)
        reports = []
        title = "Sangria" if transfer_type == TransferType.TRANSFER_CASH_OUT.value else "Suprimento"

        for transfer in transfers:
            report = StringIO()

            current_datetime = datetime.datetime.strptime(transfer.operation_date, "%Y-%m-%d %H:%M:%S")
            current_datetime = convert_from_utf_to_localtime(current_datetime).strftime('%d-%m-%Y %H:%M:%S')

            report.write(report_default_header(title, int(pos_id), operator_id, period, current_datetime, self.store_id))
            envelope_number = transfer.glaccount.split("envelope\": \"")[1].split("\"")[0]
            manager = transfer.glaccount.split("manager\": \"")[1].split("\"")[0]
            self._transfers_report_body(transfer.amount, envelope_number, manager, report)

            reports.append({current_datetime: report.getvalue()})

        return json.dumps(reports, default=lambda o: o.__dict__, sort_keys=True)

    def _transfers_report_body(self, amount, envelope_number, manager, report):
        self._write_cash_in_and_cash_out(amount, envelope_number, manager, report)

    @staticmethod
    def _write_cash_in_and_cash_out(amount, envelope_number, manager, report):
        if amount != "":
            report.write(break_line())
            report.write(add_amount_line("Valor", None, amount))
        if envelope_number != "":
            report.write(add_key_value_line("Numero Envelope..: ", envelope_number))
        if manager != "":
            report.write(add_key_value_line("Autorizado por...: ", manager))
