from _LoginSummaryHeaderDto import LoginSummaryHeaderDto  # noqa
from _LoginSummaryBodyDto import LoginSummaryBodyDto  # noqa


class LoginSummaryDto(object):
    def __init__(self, login_summary_header_dto, login_summary_body_dto):
        # type:(LoginSummaryHeaderDto, LoginSummaryBodyDto) -> ()
        self.login_summary_header_dto = login_summary_header_dto
        self.login_summary_body_dto = login_summary_body_dto
