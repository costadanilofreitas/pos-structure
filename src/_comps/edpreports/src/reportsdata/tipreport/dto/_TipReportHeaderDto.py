from datetime import datetime  # noqa


class TipReportHeaderDto(object):
    def __init__(self, start_date, end_date, current_date_time, store_id):
        # type: (datetime, datetime, datetime, store_id) -> None

        if start_date > end_date:
            raise Exception("The start_date cannot be greater than end_date")

        self.start_date = start_date  # type: datetime
        self.end_date = end_date  # type: datetime
        self.current_date_time = current_date_time  # type: datetime
        self.store_id = store_id  # type: str
