# encoding: utf-8
from escposformatter import DefaultEscPosFormatter
from mwposreport import ReporterFactory

from reportsdata.deliveryreport import DeliveryGenerator, DeliveryPresenter
from deliveryreport.repository import DeliveryOrderRepository, DeliveryProductRepository


class ReportGenerator(object):
    @staticmethod
    def generate(mb_context, pos_id, order_id, pos_list):
        if not pos_list:
            pos_list = [pos_id]
        else:
            pos_list = pos_list.split(",")
            
        order_repository = DeliveryOrderRepository(mb_context, pos_list)
        product_repository = DeliveryProductRepository(mb_context)
        report = ReporterFactory.build_reporter(pos_id,
                                                DeliveryGenerator(order_repository, product_repository, order_id),
                                                DeliveryPresenter(56)).create_base_report()
        return DefaultEscPosFormatter().format(report.get_parts())
