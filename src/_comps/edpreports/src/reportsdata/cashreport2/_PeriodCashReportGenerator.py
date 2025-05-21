from typing import Dict  # noqa
from commons.report import Generator
from .dto import CashReportDto, PeriodCashReportFilterDto, CashReportBodyDto, CashReportBodyLineDto
from domain import OperatorNameRetriever, StoreRetriever, OrderRepository, Order, \
    TransferRepository, Transfer, SessionRepository, Clock  # noqa
from commons.dto import DefaultHeaderDto


class PeriodCashReportGenerator(Generator):
    def __init__(self,
                 filter,
                 clock,
                 operator_name_retriever,
                 store_retriever,
                 order_repository,
                 transfer_repository,
                 session_repository):
        # type: (PeriodCashReportFilterDto, Clock, OperatorNameRetriever, StoreRetriever, OrderRepository, TransferRepository, SessionRepository) -> None  # noqa
        self.filter = filter
        self.clock = clock
        self.operator_name_retriever = operator_name_retriever
        self.store_retriever = store_retriever
        self.order_repository = order_repository
        self.transfer_repository = transfer_repository
        self.session_repository = session_repository

    def generate_data(self):
        # type: () -> CashReportDto
        header = self.generate_header()
        body = self.generate_body()
        return CashReportDto(header, body)

    def generate_body(self):
        body = CashReportBodyDto()
        body.operator_count = self.calculate_operator_count()
        self.fill_order_fields(body)
        self.fill_transfer_fields(body)
        body.value_in_drawer = self.calculate_value_in_drawer(body)
        return body

    def generate_header(self):
        report_type = self.filter.report_type
        store_code = self.store_retriever.get_store().code
        operator_name = None
        if self.filter.operator_id is not None:
            operator_name = self.operator_name_retriever.get_operator_name(self.filter.operator_id)
        generated_time = self.clock.get_current_datetime()
        return DefaultHeaderDto(report_type,
                                self.filter.initial_date,
                                self.filter.end_date,
                                self.filter.pos,
                                self.filter.operator_id,
                                operator_name,
                                store_code,
                                generated_time)

    def calculate_operator_count(self):
        return self.session_repository.get_unique_user_session_count(
            self.filter.initial_date,
            self.filter.end_date)

    def fill_order_fields(self, body):
        tender_dict = {}  # type: Dict[str, CashReportBodyLineDto]
        orders = self.order_repository.get_order(self.filter.initial_date,
                                                 self.filter.end_date,
                                                 self.filter.pos,
                                                 self.filter.operator_id)
        for order in orders:
            self.add_order_to_field(body.total_sales, order)

            if order.state == Order.OrderSate.voided:
                self.add_order_to_field(body.voids, order)

            if order.state == Order.OrderSate.paid:
                self.add_order_to_field(body.net_sales, order)

            for tender in order.tenders:
                self.add_tender_to_dict(tender, tender_dict)
        body.tender_breakdown = list(tender_dict.values())

    @staticmethod
    def add_order_to_field(field, order, detail=None):
        # type: (CashReportBodyLineDto, Order, str) -> None  # noqa
        field.quantity += 1
        field.value += order.total
        field.detail = detail

    @staticmethod
    def add_tender_to_dict(tender, tender_dict):
        if tender.type not in tender_dict:
            tender_dict[tender.type] = CashReportBodyLineDto(0, 0.0, tender.type)
        tender_dict[tender.type].quantity += 1
        tender_dict[tender.type].value += tender.value

    def fill_transfer_fields(self, body):
        transfers = self.transfer_repository.get_transfers(self.filter.initial_date,
                                                           self.filter.end_date)
        for transfer in transfers:
            if transfer.type == Transfer.Type.initial_float:
                self.add_transfer_to_field(body.initial_float, transfer)

            if transfer.type == Transfer.Type.cash_in:
                self.add_transfer_to_field(body.cash_ins, transfer)

            if transfer.type in (Transfer.Type.cash_out, Transfer.Type.last_cash_out):
                self.add_transfer_to_field(body.cash_outs, transfer)

    @staticmethod
    def add_transfer_to_field(field, transfer):
        # type: (CashReportBodyLineDto, Transfer) -> None
        field.quantity += 1
        field.value += transfer.value

    @staticmethod
    def calculate_value_in_drawer(body):
        value = body.initial_float.value + body.cash_ins.value
        for tender in body.tender_breakdown:
            if tender.detail == "MONEY":
                value += tender.value
        value -= body.cash_outs.value

        return value
