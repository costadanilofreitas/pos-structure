from typing import List


class TableReportFilterDto(object):
    def __init__(self, pos_id, table_id, orders):
        # type: (str, List[str]) -> None
        self.pos_id = pos_id
        self.table_id = table_id
        self.orders = orders
