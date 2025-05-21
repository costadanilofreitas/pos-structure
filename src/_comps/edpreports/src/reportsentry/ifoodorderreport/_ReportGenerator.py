# encoding: utf-8
from escposformatter import DefaultEscPosFormatter
from mwposreport import ReporterFactory

from reportsdata.ifoodorderreport import IFoodOrderGenerator, IFoodOrderPresenter


class ReportGenerator(object):
    @staticmethod
    def generate(mb_context, pos_id, order_json):
        report = ReporterFactory.build_reporter(pos_id,
                                                IFoodOrderGenerator(order_json),
                                                IFoodOrderPresenter(42)).create_base_report()
        return DefaultEscPosFormatter().format(report.get_parts())
