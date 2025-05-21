from _LogoutSummaryHeaderDto import LogoutSummaryHeaderDto  # noqa
from _LogoutSummaryBodyDto import LogoutSummaryBodyDto  # noqa


class LogoutSummaryDto(object):
    def __init__(self, logout_summary_header_dto, logout_summary_body_dto):
        # type:(LogoutSummaryHeaderDto, LogoutSummaryBodyDto) -> ()
        self.logout_summary_header_dto = logout_summary_header_dto
        self.logout_summary_body_dto = logout_summary_body_dto
