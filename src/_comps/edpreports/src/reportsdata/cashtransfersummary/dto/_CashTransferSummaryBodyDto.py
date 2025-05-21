class CashTransferSummaryBodyDto(object):
    def __init__(self, cash_out, value, envelope_number, authorizer):
        # type: (bool, float, int, unicode) -> ()
        self.cash_out = cash_out
        self.value = value
        self.envelope_number = envelope_number
        self.authorizer = authorizer
