from commons.dto import DefaultHeaderDto
from commons.report import Generator  # noqa
from commons.repository import AccountRepository  # noqa
from reports_app.cashreport.dto import CashReportDto  # noqa
from reports_app.cashreport.dto import CashReportFiltersDto  # noqa
from reports_app.cashreport.dto import CashReportBodyDto
from reports_app.cashreport.dto import CashReportBodyLineDto
from reports_app.cashreport.dto import OrderInfo


class CashReportGenerator(Generator):
    def __init__(self, account_repository, order_repository, cash_report_filter):
        # type: (AccountRepository, OrderRepository, CashReportFiltersDto) -> None
        self.account_repository = account_repository
        self.cash_report_filter = cash_report_filter
        self.order_repository = order_repository

    def generate_data(self):
        header_report_dto = self.generate_header()
        body_report_dto = self.generate_body()
        return CashReportDto(header_report_dto, body_report_dto, self.cash_report_filter.caller_pos_id)

    def generate_header(self):
        if self.cash_report_filter.report_type == 'report_by_session_id':
            date = self.cash_report_filter.initial_date.strftime("%d/%m/%Y")
        else:
            date = self.cash_report_filter.initial_date.strftime("%d/%m/%Y") + " - " + self.cash_report_filter.end_date.strftime("%d/%m/%Y")

        header_report_dto = DefaultHeaderDto(
            self.cash_report_filter.store_id,
            self.cash_report_filter.pos_id,
            self.cash_report_filter.operator_id,
            date,
            self.cash_report_filter.report_type
        )
        return header_report_dto

    def generate_body(self):
        initial_balance = CashReportBodyLineDto('$INITIAL_BALANCE', None, 0.0)
        sales = CashReportBodyLineDto('$SALES', 0, 0.0)
        voided_orders = CashReportBodyLineDto('$VOIDED_ORDERS', 0, 0.0)
        discounts = CashReportBodyLineDto('$DISCOUNTS', None, None)
        donations = CashReportBodyLineDto('$DONATIONS', 0, 0.0)
        liquid_sales = CashReportBodyLineDto('$LIQUID_SALES', 0, 0.0)
        tender_types = CashReportBodyLineDto('$TENDER_TYPES', None, None)
        cash_out = CashReportBodyLineDto('$CASH_OUT', 0, 0.0)
        cash_in = CashReportBodyLineDto('$CASH_IN', 0, 0.0)
        value_in_drawer = CashReportBodyLineDto('$VALUE_IN_DRAWER', None, 0.0)

        self.parse_account_db(cash_in, cash_out, initial_balance)
        self.parse_order_db(cash_in, cash_out, initial_balance, sales, voided_orders, liquid_sales, donations, value_in_drawer)

        return CashReportBodyDto([initial_balance,
                                  sales,
                                  voided_orders,
                                  discounts,
                                  donations,
                                  liquid_sales,
                                  tender_types,
                                  cash_out,
                                  cash_in,
                                  value_in_drawer], 'report_by_business_period')

    def parse_order_db(self, cash_in, cash_out, initial_balance, sales, voided_orders, liquid_sales, donations, value_in_drawer):
        orders_info = self.get_order_db_info()

        for item in orders_info.paid_orders:
            liquid_sales.quantity += 1
            liquid_sales.value += item.total
        if orders_info.voided_orders is not None:
            for item in orders_info.voided_orders:
                voided_orders.quantity += 1
                voided_orders.value += item.total
        for item in orders_info.paid_orders:
            if item.donation > 0:
                donations.quantity += 1
                donations.value += item.donation
        if orders_info.voided_orders is not None:
            sales.quantity = liquid_sales.quantity + voided_orders.quantity
            sales.value = liquid_sales.value + voided_orders.value

        value_in_drawer.value = initial_balance.value + cash_in.value - cash_out.value
        for item in orders_info.paid_orders:
            for item_tender in item.tenders:
                if item_tender.type == 0:
                    value_in_drawer.value += item_tender.value
            value_in_drawer.value -= item.change_amount

    def get_value_in_drawer(self):
        initial_balance = CashReportBodyLineDto(None, None, 0.0)
        cash_out = CashReportBodyLineDto(None, 0, 0.0)
        cash_in = CashReportBodyLineDto(None, 0, 0.0)

        self.cash_report_filter.report_type = 'report_by_session_id'

        self.parse_account_db(cash_in, cash_out, initial_balance)
        orders_info = self.get_order_db_info()

        value_in_drawer = initial_balance.value + cash_in.value - cash_out.value
        for item in orders_info.paid_orders:
            for item_tender in item.tenders:
                if item_tender.type == 0:
                    value_in_drawer += item_tender.value
            value_in_drawer -= item.change_amount

        return value_in_drawer

    def get_order_db_info(self):
        paid_orders = None
        voided_orders = None
        if self.cash_report_filter.report_type == 'report_by_real_date':
            paid_orders = self.order_repository.get_paid_orders_by_real_date(
                self.cash_report_filter.initial_date,
                self.cash_report_filter.end_date,
                self.cash_report_filter.operator_id,
                self.cash_report_filter.pos_id)
            voided_orders = self.order_repository.get_voided_orders_by_real_date(
                self.cash_report_filter.initial_date,
                self.cash_report_filter.end_date,
                self.cash_report_filter.operator_id,
                self.cash_report_filter.pos_id)
        if self.cash_report_filter.report_type == 'report_by_business_period':
            paid_orders = self.order_repository.get_paid_orders_by_business_period(
                self.cash_report_filter.initial_date,
                self.cash_report_filter.end_date,
                self.cash_report_filter.operator_id,
                self.cash_report_filter.pos_id)
            voided_orders = self.order_repository.get_voided_orders_by_business_period(
                self.cash_report_filter.initial_date,
                self.cash_report_filter.end_date,
                self.cash_report_filter.operator_id,
                self.cash_report_filter.pos_id)
        if self.cash_report_filter.report_type == 'report_by_session_id':
            paid_orders = self.order_repository.get_paid_orders_by_session_id(
                self.cash_report_filter.session_id)
            voided_orders = self.order_repository.get_voided_orders_by_session_id(
                self.cash_report_filter.session_id)
        if self.cash_report_filter.report_type == 'report_by_xml':
            paid_orders = self.order_repository.get_paid_orders_by_xml(
                self.cash_report_filter.initial_date,
                self.cash_report_filter.end_date)
            voided_orders = None

        return OrderInfo(paid_orders, voided_orders, "todo")

    def parse_account_db(self, cash_in, cash_out, initial_balance):
        account_info = self.get_account_db_info()

        if account_info is not None:
            for item in account_info:
                if item.transfer_cash_in_cash_out == 1 and initial_balance.value == 0.0:
                    initial_balance.value = item.transfer_value
                elif item.transfer_cash_in_cash_out == 3 or item.transfer_cash_in_cash_out == 1:
                    cash_in.quantity += 1
                    cash_in.value += item.transfer_value
                elif item.transfer_cash_in_cash_out == 4:
                    cash_out.quantity += 1
                    cash_out.value += item.transfer_value

    def get_account_db_info(self):
        account_info = None
        if self.cash_report_filter.report_type == 'report_by_real_date':
            account_info = self.account_repository.get_transfers_by_real_date(
                self.cash_report_filter.initial_date,
                self.cash_report_filter.end_date,
                self.cash_report_filter.operator_id,
                self.cash_report_filter.pos_id,
                self.cash_report_filter.report_type)
        if self.cash_report_filter.report_type == 'report_by_business_period':
            account_info = self.account_repository.get_transfers_by_business_period(
                self.cash_report_filter.initial_date,
                self.cash_report_filter.end_date,
                self.cash_report_filter.operator_id,
                self.cash_report_filter.pos_id,
                self.cash_report_filter.report_type)
        if self.cash_report_filter.report_type == 'report_by_session_id':
            account_info = self.account_repository.get_transfers_by_session_id(
                self.cash_report_filter.session_id,
                self.cash_report_filter.report_type)
        if self.cash_report_filter.report_type == 'report_by_xml':
            account_info = None
        return account_info
