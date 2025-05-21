from mw import RealClock, MwTipRepository, MwOperatorNameRetriever
from datetime import datetime

from reportsdata.tipreport import TipReportPresenter, TipReportGenerator
from reportsdata.tipreport.dto import TipReportFilterDto


class ReportGenerator(object):
    @staticmethod
    def generate(mb_context, pos_id, start_date, end_date, operator_id=None):
        start_date = datetime.strptime(start_date, "%Y%m%d")
        end_date = datetime.strptime(end_date, "%Y%m%d")

        repository = MwTipRepository(mb_context)
        operator_retriever = MwOperatorNameRetriever(mb_context)

        generator = TipReportGenerator(TipReportFilterDto(start_date, end_date, operator_id),
                                       operator_retriever,
                                       RealClock(),
                                       repository)

        return generator, TipReportPresenter()
