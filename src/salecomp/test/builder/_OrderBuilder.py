from datetime import datetime, date

from salecomp.model import State, OrderType, SaleType, Order


class OrderBuilder(object):
    def __init__(self):
        self.id = 1
        self.state = State.in_progress
        self.type = OrderType.sale
        self.originator_id = 4
        self.created_at = datetime.utcnow()
        self.business_period = date.today()
        self.pod_type = "FC"
        self.session_id = "session_id"
        self.price_lists = ['EI']
        self.price_basis = "G"
        self.sale_type = SaleType(0, "EAT_IN")
        self.lines = []

    def with_id(self, id):
        self.id = id
        return self

    def with_state(self, state):
        self.state = state
        return self

    def with_type(self, type):
        self.type = type
        return self

    def with_originator_id(self, originator_id):
        self.originator_id = originator_id
        return self

    def with_created_at(self, created_at):
        self.created_at = created_at
        return self

    def with_business_period(self, business_period):
        self.business_period = business_period
        return self

    def with_pod_type(self, pod_type):
        self.pod_type = pod_type
        return self

    def with_session_id(self, session_id):
        self.session_id = session_id
        return self

    def with_price_lists(self, price_lists):
        self.price_lists = price_lists
        return self

    def with_price_basis(self, price_basis):
        self.price_basis = price_basis
        return self

    def with_sale_type(self, sale_type):
        self.sale_type = sale_type
        return self

    def add_line(self, line):
        self.lines.append(line)
        return self

    def build(self):
        lines = []
        for line in self.lines:
            if hasattr(line, "build"):
                lines.append(line.build())
            else:
                lines.append(line)
        return Order(self.id,
                     self.state,
                     self.type,
                     self.originator_id,
                     self.created_at,
                     self.business_period,
                     self.pod_type,
                     self.session_id,
                     self.price_lists,
                     self.price_basis,
                     self.sale_type,
                     lines)
