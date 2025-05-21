import datetime  # noqa


class CashReportFiltersDto(object):
    def __init__(self, pos_id, store_id, operator_id, initial_date, end_date, report_type, session_id, caller_pos_id):
        # type: (int, int, int, datetime, datetime, unicode, unicode, id) -> None
        self.pos_id = pos_id
        self.store_id = store_id
        self.operator_id = operator_id
        self.initial_date = initial_date
        self.end_date = end_date
        self.report_type = report_type
        self.session_id = session_id
        self.caller_pos_id = caller_pos_id
