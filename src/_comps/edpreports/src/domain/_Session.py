from datetime import datetime


class Session(object):
    def __init__(self, id, pos_id, operator_id, operator_name, business_period, open_time, close_time):
        # type: (str, int, int, str, datetime, datetime, datetime) -> None
        self.id = id
        self.pos_id = pos_id
        self.operator_id = operator_id
        self.operator_name = operator_name
        self.business_period = business_period
        self.open_time = open_time
        self.close_time = close_time
