from testdoubleutil import SpyCall

from ._OrderRepositoryStub import OrderRepositoryStub


class OrderRepositorySpy(OrderRepositoryStub):
    def __init__(self, get_order_response=None):
        super(OrderRepositorySpy, self).__init__(get_order_response)
        self.get_order_call = SpyCall()
        self.add_line_call = SpyCall()
        self.update_line_call = SpyCall()
        self.delete_sons_call = SpyCall()

    def get_order(self, pos_id, order_id):
        self.get_order_call.register_call(pos_id, order_id)
        return super(OrderRepositorySpy, self).get_order(pos_id, order_id)

    def add_line(self, line):
        self.add_line_call.register_call(line)
        super(OrderRepositorySpy, self).add_line(line)

    def update_line(self, line):
        self.update_line_call.register_call(line)
        super(OrderRepositorySpy, self).update_line(line)

    def delete_sons(self, line):
        self.delete_sons_call.register_call(line)
        super(OrderRepositorySpy, self).delete_sons(line)