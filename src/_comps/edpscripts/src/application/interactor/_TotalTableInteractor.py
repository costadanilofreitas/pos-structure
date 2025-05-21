import json
from application.domain import TableService  # noqa
from xml.etree import cElementTree as eTree


class TotalTableInteractor(object):
    def __init__(self, table_service):
        # type: (TableService) -> None
        self.table_service = table_service

    def execute(self, pos_id, table_id, tip_rate, per_seat):
        # type: (str, str, str, bool) -> str
        if not per_seat:
            return self.table_service.do_total_table(pos_id, table_id, tip_rate)

        table_picture = self.table_service.get_table_picture(pos_id, table_id)
        xml = eTree.XML(table_picture)
        seat_distribution = {}
        for order_xml in xml.findall("Orders/Order"):
            for sale_line in order_xml.findall("SaleLine"):
                if sale_line.get("level") != "0" or sale_line.get("qty") == "0":
                    continue
                if sale_line.get("customProperties") is None:
                    raise Exception("To divide by seat, all items must be in a valid seat")
                else:
                    custom_properties = sale_line.get("customProperties")
                    cp_dict = json.loads(custom_properties)
                    seat = cp_dict["seat"]
                    if seat == "0":
                        raise Exception("To divide by seat, all items must be in a valid seat")

                    if seat not in seat_distribution:
                        seat_distribution[seat] = []

                    order_dict = None
                    for order in seat_distribution[seat]:
                        if order["originalOrderId"] == order_xml.get("orderId"):
                            order_dict = order
                            break
                    if order_dict is None:
                        order_dict = {
                            "originalOrderId": order_xml.get("orderId"),
                            "lineNumbers": []
                        }
                        seat_distribution[seat].append(order_dict)

                    order_dict["lineNumbers"].append(int(sale_line.get("lineNumber")))

        return self.table_service.do_total_table(pos_id, table_id, tip_rate, json.dumps(seat_distribution))
