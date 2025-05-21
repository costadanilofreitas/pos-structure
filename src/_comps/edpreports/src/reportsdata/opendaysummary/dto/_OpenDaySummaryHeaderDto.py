class OpenDaySummaryHeaderDto(object):
    def __init__(self, pos_id, store_id, operator_id, business_date):
        # type: (int, int, int, unicode) -> ()
        self.pos_id = pos_id
        self.store_id = store_id
        self.operator_id = operator_id
        self.business_date = business_date
