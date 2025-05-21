from commons.dto import DefaultHeaderDto  # noqa
from _TransfersByDayDto import TransfersByDayDto  # noqa


class CashTransferReportDto(object):
    def __init__(self, header_transfer_dto, all_transfers_dto, pos_id):
        # type: (DefaultHeaderDto, [TransfersByDayDto]) -> None
        self.header_transfer_dto = header_transfer_dto
        self.all_transfers_dto = all_transfers_dto
        self.pos_id = pos_id
