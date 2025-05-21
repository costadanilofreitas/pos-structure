from _CloseDaySummaryHeaderDto import CloseDaySummaryHeaderDto  # noqa
from _CloseDaySummaryBodyDto import CloseDaySummaryBodyDto  # noqa


class CloseDaySummaryDto(object):
    def __init__(self, close_day_summary_header_dto, close_day_summary_body_dto):
        # type:(CloseDaySummaryHeaderDto, CloseDaySummaryBodyDto) -> ()
        self.close_day_summary_header_dto = close_day_summary_header_dto
        self.close_day_summary_body_dto = close_day_summary_body_dto
