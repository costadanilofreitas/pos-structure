from commons.report import Generator
from reports_app.cashtransfersummary.dto import CashTransferSummaryInfo  # noqa
from reports_app.cashtransfersummary.dto import CashTransferSummaryDto
from reports_app.cashtransfersummary.dto import CashTransferSummaryHeaderDto
from reports_app.cashtransfersummary.dto import CashTransferSummaryBodyDto


class CashTransferGenerator(Generator):
    def __init__(self, cash_transfer_summary_info):
        # type: (CashTransferSummaryInfo) -> ()
        self.cash_transfer_summary_info = cash_transfer_summary_info

    def generate_data(self):
        # type: (CashTransferSummaryInfo) -> CashTransferSummaryDto
        cash_transfer_summary_header_dto = CashTransferSummaryHeaderDto(
            self.cash_transfer_summary_info.cash_out,
            self.cash_transfer_summary_info.pos_id,
            self.cash_transfer_summary_info.store_id,
            self.cash_transfer_summary_info.operator_id,
            self.cash_transfer_summary_info.business_date
        )
        cash_transfer_summary_body_dto = CashTransferSummaryBodyDto(
            self.cash_transfer_summary_info.cash_out,
            self.cash_transfer_summary_info.value,
            self.cash_transfer_summary_info.envelope_number,
            self.cash_transfer_summary_info.authorizer
        )

        return CashTransferSummaryDto(cash_transfer_summary_header_dto, cash_transfer_summary_body_dto)
