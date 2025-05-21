from datetime import datetime  # noqa


class TipReportFilterDto(object):
    def __init__(self, start_date=None, end_date=None, operator_id=None):
        # type: (datetime, datetime, str) -> None
        self.start_date = start_date
        self.end_date = end_date
        self.operator_id = operator_id
