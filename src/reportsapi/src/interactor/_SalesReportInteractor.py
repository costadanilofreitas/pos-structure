from sysactions import generate_report
from datetime import datetime
import json


class SalesReportInteractor:
    def __init__(self, store_id):
        self.store_id = store_id

    def dayle_sales_report(self, data):
        formatted_date = datetime.strptime(data, '%Y%m%d').strftime("%Y-%m-%d")
        orders = generate_report("generate_paid_order_cash_report_by_date", data, data)
        orders = json.loads(orders)

        total = 0
        for order in orders:
            total += order["total"]

        return {"store": self.store_id, "ip":"localhost", "date": formatted_date, "sales": total}

    def dayle_sales_orders(self, date):

        # formatted_date = datetime.strptime(date, '%Y%m%d').strftime("%Y-%m-%d")
        orders = generate_report("generate_paid_order_cash_report_by_date", date, date)
        orders = json.loads(orders)
        return orders
