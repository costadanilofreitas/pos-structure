# encoding: utf-8
import time
from cStringIO import StringIO
from datetime import datetime
from xml.etree import cElementTree as eTree

from mw import MsgBusTableService as tableService
from old_helper import convert_from_utf_to_localtime
from utils import report_default_header, DATE_TIME_FMT, center, add_key_value_line, empty_line, add_table_line, \
    get_store_id


class OpenedTablesReport(object):
    def __init__(self, table_repository, pos_id, operator_name_retriever):
        self.table_repository = table_repository
        self.pos_id = pos_id
        self.operator_name_retriever = operator_name_retriever
        self.store_id = get_store_id()

    def generate_opened_tables_report(self, pos_id):
        report = StringIO()
        title = "Relatorio de mesas abertas"
        current_datetime = time.strftime(DATE_TIME_FMT)
        report.write(report_default_header(title, int(pos_id), None, None, current_datetime, self.store_id))
        self._opened_tabes_report_body(report)

        return report.getvalue()

    def _opened_tabes_report_body(self, report):
        tables = self.table_repository.get_opened_tables()

        for table_id in tables:
            table_picture = tableService().get_table_picture(self.pos_id, str(table_id))
            table_picture_xml = eTree.XML(table_picture)
            table_orders = table_picture_xml.findall(".//Order")
            table_amount = sum([float(order.get("totalAmount")) for order in table_orders])
            date = datetime.strptime(table_picture_xml.get("startTS"), "%Y-%m-%d %H:%M:%S")
            date = convert_from_utf_to_localtime(date)
            operator_id = table_picture_xml.get("userId")
            operator_name = self.operator_name_retriever.get_operator_name(operator_id)
            seats = table_picture_xml.get("seats")

            columns = ["Total [Assentos]", 'R$ {:>8.2f}'.format(table_amount) + " [" + seats + "]"]
            columns_height = [18, 20]
            character_to_add = [".:", " ", " "]
            is_tab = "TAB" in table_id
            table_context = "Comanda " if is_tab else "Mesa "
            table_id = table_picture_xml.find("Properties").get("TAB_ID") if is_tab else table_id

            report.write(center(table_context + str(table_id) + " - " + datetime.strftime(date, "%d/%m/%Y %H:%M:%S")))
            report.write(add_key_value_line("Operador........: ", operator_name))
            report.write(add_table_line(columns, columns_height, character_to_add=character_to_add))
            report.write(empty_line())
