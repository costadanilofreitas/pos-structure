class CashTransferSummaryHeaderDto(object):
    def __init__(self, cash_out, pos_id, store_id, operator_id, business_date):
        # type: (bool, int, int, int, unicode) -> ()
        self.cash_out = cash_out
        self.pos_id = pos_id
        self.store_id = store_id
        self.operator_id = operator_id
        self.business_date = business_date
