from datetime import datetime

from orderdumper import MultipleDatabaseExecutor, OrderRepository, OrderFormatter


def main():
    executor = \
        MultipleDatabaseExecutor("D:\\Projects\\e-Deploy\\pos-structure\\mwdatas\\data.client\\server\\databases")

    orders = []
    def inner_func(order_repository):
        # type: (OrderRepository) -> None
        orders.extend(order_repository.get_paid_orders(datetime(2019, 11, 4)))

    executor.execute(inner_func, OrderRepository)
    ret = ""
    order_formatter = OrderFormatter()
    for order in orders:
        ret += order_formatter.format(order) + "\r\n"

    print(ret)


main()
