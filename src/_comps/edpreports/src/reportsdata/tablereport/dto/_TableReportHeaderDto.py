from datetime import datetime


class TableReportHeaderDto(object):

    def __init__(self):
        self.table_id = None  # type: str
        self.service_seats = None  # type: int
        self.start_date = None  # type: datetime
        self.totaled_date = None  # type: datetime
        self.user_id = None  # type: str
        self.user_name = None  # type: str
