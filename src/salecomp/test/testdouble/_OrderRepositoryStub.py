from salecomp.repository import OrderRepository


class OrderRepositoryStub(OrderRepository):
    def __init__(self, get_order_response=None):
        self.get_order_response = get_order_response

    def get_order(self, pos_id, order_id):
        return self.get_order_response

    def add_line(self, line):
        pass

    def update_line(self, line):
        pass

    def delete_sons(self, line):
        pass
