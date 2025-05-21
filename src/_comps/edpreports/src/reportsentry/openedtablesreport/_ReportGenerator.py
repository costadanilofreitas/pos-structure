# encoding: utf-8
from mw import MwOperatorNameRetriever

from openedtablesreport import OpenedTablesReport
from openedtablesreport.repository import TableRepository


class ReportGenerator(object):
    @staticmethod
    def generate(mb_context, pos_id):
        operator_retriever = MwOperatorNameRetriever(mb_context)
        table_repository = TableRepository(mb_context, pos_id)
        opened_tables_report_generator = OpenedTablesReport(table_repository, pos_id, operator_retriever)
        return opened_tables_report_generator.generate_opened_tables_report(pos_id)

