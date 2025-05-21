from commons.dto import DefaultHeaderDto
from commons.report import Generator
from reports_app.cashtransferreport.dto import CashTransferReportDto  # noqa
from reports_app.cashtransferreport.dto import CashReportFiltersDto  # noqa
from reports_app.cashtransferreport.dto import TransfersByDayDto


class CashTransferGenerator(Generator):
    def __init__(self, account_repository, cash_transfer_filter):
        # type: (AccountRepository, CashReportFiltersDto) -> None
        self.account_repository = account_repository
        self.cash_transfer_filter = cash_transfer_filter

    def generate_data(self):
        header_transfer_dto = DefaultHeaderDto(
            self.cash_transfer_filter.store_id,
            self.cash_transfer_filter.pos_id,
            self.cash_transfer_filter.operator_id,
            self.cash_transfer_filter.initial_date.strftime("%d/%m/%Y") + " - " +
            self.cash_transfer_filter.end_date.strftime("%d/%m/%Y"),
            self.cash_transfer_filter.report_type)

        transfers = self.account_repository.get_transfers_by_business_period(
            self.cash_transfer_filter.initial_date,
            self.cash_transfer_filter.end_date,
            self.cash_transfer_filter.operator_id,
            self.cash_transfer_filter.pos_id,
            self.cash_transfer_filter.report_type)

        all_transfers_dto = self._append_transfer_in_transfers_list(transfers)

        return CashTransferReportDto(header_transfer_dto, all_transfers_dto, self.cash_transfer_filter.caller_pos_id)

    def _append_transfer_in_transfers_list(self, transfers):
        all_transfers_dto = []
        for transfer in transfers:
            transfer_date = self._get_datetime_date(transfer.transfer_date)
            element_found = self._if_transfer_day_exists_insert_transfer(all_transfers_dto, transfer, transfer_date)
            self._create_new_transfer_day(all_transfers_dto, element_found, transfer, transfer_date)

        return all_transfers_dto

    @staticmethod
    def _create_new_transfer_day(all_transfers_dto, element_found, transfer, transfer_date):
        if not element_found:
            all_transfers_dto.append(TransfersByDayDto(
                transfer_date, [transfer]
            ))

    @staticmethod
    def _if_transfer_day_exists_insert_transfer(all_transfers_dto, transfer, transfer_date):
        element_found = False

        for transfer_by_day in all_transfers_dto:
            if transfer_by_day.day == transfer_date:
                transfer_by_day.transfers_by_date.append(transfer)
                element_found = True
                break
        return element_found

    @staticmethod
    def _get_datetime_date(time):
        return time.strftime("%d/%m/%Y")
