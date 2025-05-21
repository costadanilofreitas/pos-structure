from _CashReportBodyDto import CashReportBodyDto  # noqa


class CloseDaySummaryBodyDto(object):
    def __init__(self, authorizer, open_day_time, report_body):
        # type: (unicode, unicode, CashReportBodyDto) -> ()
        self.authorizer = authorizer
        self.open_day_time = open_day_time
        self.report_body = report_body
