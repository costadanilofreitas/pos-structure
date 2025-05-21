class StoreGoalsCache(object):
    def __init__(self, start_date, end_date, total_sales, average_sale_value):
        self.start_date = start_date
        self.end_date = end_date
        self.total_sales = total_sales
        self.average_sale_value = average_sale_value
        self.operator_sale_value = 0
