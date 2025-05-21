from _CashReportBodyDto import CashReportBodyDto  # noqa


class LogoutSummaryBodyDto(object):
    def __init__(self, authorizer, login_time, report_body):
        # type: (float, unicode, unicode, CashReportBodyDto) -> ()
        self.authorizer = authorizer
        self.login_time = login_time
        self.report_body = report_body
