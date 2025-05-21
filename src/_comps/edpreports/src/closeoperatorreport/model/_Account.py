class Account(object):
    def __init__(self, account_type, amount, tender_id, operation_date, glaccount):
        self.account_type = account_type
        self.amount = amount
        self.tender_id = tender_id
        self.operation_date = operation_date
        self.glaccount = glaccount
