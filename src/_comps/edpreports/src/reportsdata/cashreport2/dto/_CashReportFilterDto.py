from abc import ABCMeta


class CashReportFilterDto(object):
    __metaclass__ = ABCMeta

    def __init__(self, report_type):
        # type: (str) -> None
        self.report_type = report_type
