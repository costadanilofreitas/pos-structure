from _OpenDaySummaryHeaderDto import OpenDaySummaryHeaderDto  # noqa
from _OpenDaySummaryBodyDto import OpenDaySummaryBodyDto  # noqa


class OpenDaySummaryDto(object):
    def __init__(self, open_day_summary_header_dto, open_day_summary_body_dto):
        # type:(OpenDaySummaryHeaderDto, OpenDaySummaryBodyDto) -> ()
        self.open_day_summary_header_dto = open_day_summary_header_dto
        self.open_day_summary_body_dto = open_day_summary_body_dto
