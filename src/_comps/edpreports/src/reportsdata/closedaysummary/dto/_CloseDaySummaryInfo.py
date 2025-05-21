class CloseDaySummaryInfo(object):
    def __init__(self, pos_id, store_id, operator_id, business_date, authorizer, open_day_time, initial_date, end_date):
        # type: (int, int, int, unicode, float, unicode, unicode, unicode) -> ()
        self.pos_id = pos_id
        self.store_id = store_id
        self.operator_id = operator_id
        self.business_date = business_date
        self.authorizer = authorizer
        self.open_day_time = open_day_time
        self.initial_date = initial_date
        self.end_date = end_date
