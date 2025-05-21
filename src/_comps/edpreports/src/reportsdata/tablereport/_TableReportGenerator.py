import cfgtools
import os

from domain import Clock, TableOrderRetriever, TableOrderSaleLine, TableOrder, Table
from old_helper import convert_from_utf_to_localtime
from report import Generator
from typing import List

from dto import \
    TableReportFilterDto, \
    TableReportDto, \
    TableReportBodyDto, \
    TableReportHeaderDto, \
    TableReportOrderDto, \
    TableReportSaleLineDto


class TableReportGenerator(Generator):

    def __init__(self, filters, clock, table_order_retriever):
        # type: (TableReportFilterDto, Clock, TableOrderRetriever) -> None
        self.filters = filters
        self.clock = clock
        self.table_order_retriever = table_order_retriever

    def generate_data(self):
        # type: () -> TableReportDto
        table = self.table_order_retriever.get_table_order(self.filters.pos_id, self.filters.table_id)

        config = cfgtools.read(os.environ["LOADERCFG"])
        show_priceless_items_config = config.find_value("PrintConfigurations.ShowPricelessItems") or 'true'
        show_priceless_items = show_priceless_items_config.lower().strip() == "true"

        header = self._generate_header(table)
        body = self._generate_body(table, show_priceless_items)

        return TableReportDto(header, body)

    def _generate_header(self, table):
        # type: (Table) -> TableReportHeaderDto
        table_report_header_dto = TableReportHeaderDto()

        table_report_header_dto.table_id = table.table_id
        table_report_header_dto.service_seats = table.service_seats
        table_report_header_dto.start_date = convert_from_utf_to_localtime(table.start_date)
        table_report_header_dto.totaled_date = self.clock.get_current_datetime()
        table_report_header_dto.user_id = table.user_id
        table_report_header_dto.user_name = table.user_name

        return table_report_header_dto

    def _generate_body(self, table, show_priceless_items):
        # type: (Table, bool) -> TableReportBodyDto
        body = TableReportBodyDto()

        body.total_per_seat = table.total_per_seat
        body.total_amount = table.total_amount
        body.sub_total_amount = table.sub_total_amount
        body.service_seats = table.service_seats
        body.tip = table.tip
        body.discount_amount = table.total_discounts

        body.orders = self._fill_orders_dto(table.orders, show_priceless_items)

        return body

    def _fill_orders_dto(self, table_orders, show_priceless_items):
        # type: (List[TableOrder], bool) -> List[TableReportOrderDto]
        table_order_dto_list = []  # type: List[TableReportOrderDto]

        for table_order in table_orders:
            table_report_order_dto = TableReportOrderDto()
            table_report_order_dto.order_id = table_order.order_id
            table_report_order_dto.discount_amount = table_order.discount_amount
            table_report_order_dto.total_after_discount = table_order.total_after_discount
            table_report_order_dto.total_amount = table_order.total_amount
            table_report_order_dto.total_tender = table_order.total_tender
            table_report_order_dto.split_key = table_order.split_key
            table_report_order_dto.tip = table_order.tip

            table_report_sales_line_dto_list = self._fill_sales_line_dto(table_order.sales_line, show_priceless_items)
            table_report_order_dto.sales_line_list = table_report_sales_line_dto_list

            table_order_dto_list.append(table_report_order_dto)

        return table_order_dto_list

    def _fill_sales_line_dto(self, table_order_sales_line, show_priceless_items):
        #  type: (List[TableOrderSaleLine], bool) -> List[TableReportSaleLineDto]
        table_report_sales_line_dto_list = []

        for sale_line in table_order_sales_line:
            if sale_line.qty > 0 and (sale_line.price > 0 or show_priceless_items):
                table_report_sale_line_dto = self._convert_table_order_sale_line_to_sale_line_dto(sale_line)
                table_report_sales_line_dto_list.append(table_report_sale_line_dto)

        return table_report_sales_line_dto_list

    @staticmethod
    def _convert_table_order_sale_line_to_sale_line_dto(table_order_sale_line):
        # type: (TableOrderSaleLine) -> TableReportSaleLineDto
        table_report_sale_line_dto = TableReportSaleLineDto()

        table_report_sale_line_dto.product_name = table_order_sale_line.product_name
        table_report_sale_line_dto.qty = table_order_sale_line.qty
        table_report_sale_line_dto.default_qty = table_order_sale_line.default_qty
        table_report_sale_line_dto.price = table_order_sale_line.price
        table_report_sale_line_dto.item_type = table_order_sale_line.item_type
        table_report_sale_line_dto.seat = table_order_sale_line.seat
        table_report_sale_line_dto.level = table_order_sale_line.level
        table_report_sale_line_dto.comment = table_order_sale_line.comment
        table_report_sale_line_dto.line_number = table_order_sale_line.line_number

        return table_report_sale_line_dto
