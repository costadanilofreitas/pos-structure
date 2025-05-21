class OpenDaySummaryInfo(object):
    def __init__(self, pos_id, store_id, operator_id, business_date, authorizer):
        # type: (int, int, int, unicode, float, unicode, unicode) -> ()
        self.pos_id = pos_id
        self.store_id = store_id
        self.operator_id = operator_id
        self.business_date = business_date
        self.authorizer = authorizer
