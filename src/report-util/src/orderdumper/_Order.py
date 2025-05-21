class Order(object):
    def __init__(self, order_id, state_id, total_gross, total_net, discount_amount, tip):
        self.order_id = order_id
        self.state_id = state_id
        self.total_gross = total_gross
        self.total_net = total_net
        self.discount_amount = discount_amount
        self.tip = tip
