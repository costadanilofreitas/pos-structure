class Payment:
    def __init__(self, payment_id, name, currency, change_limit, electronic_type, open_drawer, parent_id):
        # type: (int, str, str, float, int, int, int) -> None

        self.payment_id = payment_id
        self.name = name
        self.currency = currency
        self.change_limit = change_limit
        self.electronic_type = electronic_type
        self.open_drawer = open_drawer
        self.parent_id = parent_id
