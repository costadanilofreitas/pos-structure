from commons.report import Generator
from reports_app.loginsummary.dto import LoginSummaryInfo  # noqa
from reports_app.loginsummary.dto import LoginSummaryDto  # noqa
from reports_app.loginsummary.dto import LoginSummaryHeaderDto  # noqa
from reports_app.loginsummary.dto import LoginSummaryBodyDto


class LoginGenerator(Generator):
    def __init__(self, login_summary_info):
        # type: (LoginSummaryInfo) -> ()
        self.login_summary_info = login_summary_info

    def generate_data(self):
        # type: (LoginSummaryInfo) -> LoginSummaryDto
        login_summary_header_dto = LoginSummaryHeaderDto(
            self.login_summary_info.pos_id,
            self.login_summary_info.store_id,
            self.login_summary_info.operator_id,
            self.login_summary_info.business_date
        )
        login_summary_body_dto = LoginSummaryBodyDto(
            self.login_summary_info.initial_value,
            self.login_summary_info.pos_type,
            self.login_summary_info.authorizer
        )

        return LoginSummaryDto(login_summary_header_dto, login_summary_body_dto)
