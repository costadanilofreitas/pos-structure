from old_helper import convert_from_localtime_to_utc
from typing import List

from commons.report import Generator
from domain import Clock, OperatorTip, TipRepository, OperatorNameRetriever
from utils import get_store_id

from .dto import \
    TipReportDto, \
    TipReportFilterDto, \
    TipReportHeaderDto, \
    TipReportBodyDto, \
    TipReportDetailLineDto


class TipReportGenerator(Generator):
    def __init__(self, filter, operator_name_retriever, clock, tip_repository):
        # type: (TipReportFilterDto, OperatorNameRetriever, Clock, TipRepository) -> None
        self.filter = filter
        self.clock = clock
        self.tip_repository = tip_repository
        self.operator_name_retriever = operator_name_retriever

    def generate_data(self):
        # type: () -> TipReportDto
        header = self._generate_header()
        body = self._generate_body()
        return TipReportDto(header, body)

    def _generate_header(self):
        # type: () -> TipReportHeaderDto
        return TipReportHeaderDto(
            self.filter.start_date,
            self.filter.end_date,
            self.clock.get_current_datetime(),
            get_store_id()
        )

    def _generate_body(self):
        # type: () -> TipReportBodyDto

        tip_report_body_dto = TipReportBodyDto()

        start_date = self.filter.start_date.replace(hour=00, minute=00, second=00)
        start_date = convert_from_localtime_to_utc(start_date)

        end_date = self.filter.end_date.replace(hour=23, minute=59, second=59)
        end_date = convert_from_localtime_to_utc(end_date)

        operator_tip_list = self.tip_repository.get_tips_per_operator(
            start_date,
            end_date,
            self.filter.operator_id)

        operators = set(map(lambda x: x.operator, operator_tip_list))
        grouped_operators_with_tip_records = [[y for y in operator_tip_list if y.operator == x] for x in operators]

        for operator_with_tip_records in grouped_operators_with_tip_records:
            tip_report_detail_line = self._convert_operator_tip_list_to_tip_report_detail_line_dto(
                operator_with_tip_records)
            tip_report_body_dto.add_detail_line(tip_report_detail_line)

        return tip_report_body_dto

    def _convert_operator_tip_list_to_tip_report_detail_line_dto(self, operator_tip_list):
        # type: (List[OperatorTip]) -> TipReportDetailLineDto

        operator_name = self.operator_name_retriever.get_operator_name(operator_tip_list[0].operator)

        tables_count = len(set(map(lambda o_tip: o_tip.service_id, operator_tip_list)))
        order_count = len(operator_tip_list)
        total_order_amount = sum([order_amount.default_unit_price for order_amount in operator_tip_list])
        total_tip_amount = sum(
            [(order_amount.default_unit_price * order_amount.tip_portion) for order_amount in operator_tip_list])
        return TipReportDetailLineDto(
            operator_name,
            tables_count,
            order_count,
            round(total_order_amount, 2),
            round(total_tip_amount, 2)
        )
