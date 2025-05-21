from typing import List

from ._TipReportDetailLineDto import TipReportDetailLineDto


class TipReportBodyDto(object):
    def __init__(self):
        # type: () -> None
        self.__detail_line_list = []
        self.__total_tables_count = 0
        self.__total_order_count = 0
        self.__total_sold_amount = 0.0
        self.__total_tip_amount = 0.0

    @property
    def total_tables_count(self):
        # type: () -> str
        return str(self.__total_tables_count)

    @property
    def total_order_count(self):
        # type: () -> str
        return str(self.__total_order_count)

    @property
    def total_sold_amount(self):
        # type: () -> str
        return str(self.__total_sold_amount)

    @property
    def total_tip_amount(self):
        # type: () -> str
        return str(self.__total_tip_amount)

    @property
    def detail_line_list(self):
        # type: () -> List[TipReportDetailLineDto]
        return self.__detail_line_list

    def add_detail_line(self, tip_report_detail_line_dto):
        # type: (TipReportDetailLineDto) -> None

        self.__total_tables_count += int(tip_report_detail_line_dto.table_count)
        self.__total_order_count += int(tip_report_detail_line_dto.order_count)
        self.__total_sold_amount += round(float(tip_report_detail_line_dto.total_sold_amount), 2)
        self.__total_tip_amount += round(float(tip_report_detail_line_dto.tip_amount), 2)

        self.detail_line_list.append(tip_report_detail_line_dto)
