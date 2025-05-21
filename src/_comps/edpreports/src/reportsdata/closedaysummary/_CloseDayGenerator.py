from commons.report import Generator
from reports_app.closedaysummary.dto import CloseDaySummaryInfo  # noqa
from reports_app.closedaysummary.dto import CloseDaySummaryDto  # noqa
from reports_app.closedaysummary.dto import CloseDaySummaryHeaderDto  # noqa
from reports_app.closedaysummary.dto import CloseDaySummaryBodyDto
from reports_app.closedaysummary.dto import CashReportBodyLineDto
from reports_app.closedaysummary.dto import OrderInfo


class CloseDayGenerator(Generator):
    def __init__(self, account_repository, order_repository, close_day_summary_info):
        # type: (AccountRepository, OrderRepository, CloseDaySummaryInfo) -> ()
        self.close_day_summary_info = close_day_summary_info
        self.account_repository = account_repository
        self.order_repository = order_repository

    def generate_data(self):
        # type: (CloseDaySummaryInfo) -> CloseDaySummaryDto
        close_day_summary_header_dto = CloseDaySummaryHeaderDto(
            self.close_day_summary_info.pos_id,
            self.close_day_summary_info.store_id,
            self.close_day_summary_info.operator_id,
            self.close_day_summary_info.business_date
        )
        close_day_summary_body_dto = self.generate_body()

        return CloseDaySummaryDto(close_day_summary_header_dto, close_day_summary_body_dto)

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
        self.parse_order_db(cash_in, cash_out, initial_balance, sales, voided_orders, liquid_sales, donations,
                            value_in_drawer)

        return CloseDaySummaryBodyDto(
            self.close_day_summary_info.authorizer,
            self.close_day_summary_info.open_day_time,
            [initial_balance,
             sales,
             voided_orders,
             discounts,
             donations,
             liquid_sales,
             tender_types,
             cash_out,
             cash_in,
             value_in_drawer])

    def parse_order_db(self, cash_in, cash_out, initial_balance, sales, voided_orders, liquid_sales, donations, value_in_drawer):
        orders_info = self.get_order_db_info()

        for item in orders_info.paid_orders:
            liquid_sales.quantity += 1
            liquid_sales.value += item.total
        for item in orders_info.voided_orders:
            voided_orders.quantity += 1
            voided_orders.value += item.total
        for item in orders_info.paid_orders:
            if item.donation > 0:
                donations.quantity += 1
                donations.value += item.donation
        sales.quantity = liquid_sales.quantity + voided_orders.quantity
        sales.value = liquid_sales.value + voided_orders.value

        value_in_drawer.value = initial_balance.value + cash_in.value - cash_out.value
        for item in orders_info.paid_orders:
            for item_tender in item.tenders:
                if item_tender.type == 0:
                    value_in_drawer.value += item_tender.value
            value_in_drawer.value -= item.change_amount

    def get_order_db_info(self):
        paid_orders = self.order_repository.get_paid_orders_by_real_date(
            self.close_day_summary_info.initial_date,
            self.close_day_summary_info.end_date,
            self.close_day_summary_info.operator_id,
            self.close_day_summary_info.pos_id)
        voided_orders = self.order_repository.get_voided_orders_by_real_date(
            self.close_day_summary_info.initial_date,
            self.close_day_summary_info.end_date,
            self.close_day_summary_info.operator_id,
            self.close_day_summary_info.pos_id)

        return OrderInfo(paid_orders, voided_orders, "")

    def parse_account_db(self, cash_in, cash_out, initial_balance):
        account_info = self.get_account_db_info()

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
        account_info = self.account_repository.get_transfers_by_real_date(
            self.close_day_summary_info.initial_date,
            self.close_day_summary_info.end_date,
            self.close_day_summary_info.operator_id,
            self.close_day_summary_info.pos_id,
            'report_by_real_date')
        return account_info
