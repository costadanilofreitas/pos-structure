# COMMENT HERE
import json


class AverageTicketReport(object):
    def __init__(self, table_repository, order_repository):
        self.table_repository = table_repository
        self.order_repository = order_repository

    def generate_tickets_report(self, business_period):
        return self._generate_tickets_report(business_period)

    def _generate_tickets_report(self, business_period):
        user_table_orders = self.table_repository.get_paid_ticket(business_period)
        user_orders = self.order_repository.get_paid_orders(business_period.replace("-", ""))

        average_ticket_report = {}
        for table_order in user_table_orders:
            user = table_order[0]
            quantity = int(table_order[1])
            average_ticket_report[user] = quantity

        for order in user_orders:
            if order[0] is None:
                continue

            user = order[0].split("user=")[1].split(",")[0]
            quantity = int(order[1])
            if user in average_ticket_report:
                average_ticket_report[user] += quantity
                continue
            average_ticket_report[user] = quantity

        report = json.dumps(average_ticket_report, default=lambda o: o.__dict__, sort_keys=True)
        report_bytes = report.encode("utf-8")

        return report_bytes
