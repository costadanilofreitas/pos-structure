class CashTransferSummaryInfo(object):
    def __init__(self, cash_out, pos_id, store_id, operator_id, business_date, value, envelope_number, authorizer):
        # type: (bool, int, int, int, unicode, float, int, unicode) -> ()
        self.cash_out = cash_out
        self.pos_id = pos_id
        self.store_id = store_id
        self.operator_id = operator_id
        self.business_date = business_date
        self.value = value
        self.envelope_number = envelope_number
        self.authorizer = authorizer
