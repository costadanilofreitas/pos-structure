from mw import MwTableOrderRetriever, MsgBusTableService, RealClock
from reportsdata.tablereport import TableReportPresenter, TableReportGenerator
from reportsdata.tablereport.dto import TableReportFilterDto


class ReportGenerator(object):
    @staticmethod
    def generate(mb_context, pos_id, table_id, print_pre_account_by="TABLE", hide_unpriced_items="True"):
        table_order_retriever = MwTableOrderRetriever(MsgBusTableService())

        hide_unpriced_items = True if hide_unpriced_items == "True" else False

        generator = TableReportGenerator(TableReportFilterDto(pos_id, table_id, None),
                                         RealClock(),
                                         table_order_retriever)
        presenter = TableReportPresenter(print_pre_account_by, hide_unpriced_items)

        return generator, presenter
