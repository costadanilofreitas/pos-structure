# encoding: utf-8
import json

from hourlysalesreport import HourlySalesReport
from hourlysalesreport.repository import OrderRepository as HourlySalesOrderRepository


class ReportGenerator(object):
    @staticmethod
    def generate(mb_context, pos_id, pos_list, operator_id, period):
        pos_list = json.loads(pos_list)
        hourly_sales_report_generator = HourlySalesReport(HourlySalesOrderRepository(mb_context, pos_list))
        return hourly_sales_report_generator.generate_hourly_sales_report(pos_id, operator_id, period)

