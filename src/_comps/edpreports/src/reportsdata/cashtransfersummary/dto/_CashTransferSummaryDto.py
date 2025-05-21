from _CashTransferSummaryHeaderDto import CashTransferSummaryHeaderDto  # noqa
from _CashTransferSummaryBodyDto import CashTransferSummaryBodyDto  # noqa


class CashTransferSummaryDto(object):
    def __init__(self, cash_transfer_summary_header_dto, cash_transfer_summary_body_dto):
        # type:(CashTransferSummaryHeaderDto, CashTransferSummaryBodyDto) -> ()
        self.cash_transfer_summary_header_dto = cash_transfer_summary_header_dto
        self.cash_transfer_summary_body_dto = cash_transfer_summary_body_dto
