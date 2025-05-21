class TipReportDetailLineDto(object):
    def __init__(self, operator, table_count, order_count, total_sold_amount, tip_amount):
        # type: (str, int, int, float, float) -> None
        self.__operator = operator
        self.__table_count = table_count
        self.__order_count = order_count
        self.__total_sold_amount = total_sold_amount
        self.__tip_amount = tip_amount

    @property
    def operator(self):
        # type: () -> str
        return str(self.__operator)

    @property
    def table_count(self):
        # type: () -> str
        return str(self.__table_count)

    @property
    def order_count(self):
        # type: () -> str
        return str(self.__order_count)

    @property
    def total_sold_amount(self):
        # type: () -> str
        return str(self.__total_sold_amount)

    @property
    def tip_amount(self):
        # type: () -> str
        return str(self.__tip_amount)
