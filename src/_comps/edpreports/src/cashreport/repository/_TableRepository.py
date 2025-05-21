from cashreport.model import Order
from old_helper import BaseRepository
from typing import Dict, List


class TableRepository(BaseRepository):
    def __init__(self, mbcontext):
        super(TableRepository, self).__init__(mbcontext)

    def get_sales_average_info(self, start_date, end_date, operator_id):
        def inner_func(conn):
            cursor = conn.select(self._AverageInfoBetweenPeriodsQuery.format(start_date.strftime("%Y%m%d"),
                                                                             end_date.strftime("%Y%m%d"),
                                                                             operator_id or ""))

            average_info = TableSalesAverageInfo()
            response = cursor.get_row(0)
            if response:
                average_info.total_tables = int(response.get_entry("TotalTables") or 0)
                average_info.total_customers = int(response.get_entry("TotalCustomers") or 0)
                average_info.table_time_average_milliseconds = int(round(float(response.get_entry("TableTimeAverageMilliseconds") or 0)))

            return average_info

        return self.execute_with_connection(inner_func)

    _AverageInfoBetweenPeriodsQuery = """
    select count(TableId) as TotalTables, 
    sum(numberofseats) as TotalCustomers,
    avg((julianday(FinishedTS) - julianday(StartTS)) * 86400000) as TableTimeAverageMilliseconds
    from  tableservice tsvc
    join (select serviceid, userid from serviceorders group by serviceid) so
	on so.serviceid = tsvc.serviceid
    where strftime('%Y%m%d', tsvc.BusinessPeriod, 'utc') >= '{}' and strftime('%Y%m%d', tsvc.BusinessPeriod, 'utc') <= '{}'
    and tsvc.serviceid in (select DISTINCT serviceid from ServiceTenders) 
    and finishedts is not null
    and so.UserId like '%{}%'"""

    def get_tables_by_sector(self, orders):
        # type: (List[Order]) -> Dict
        def inner_func(conn):
            order_ids = "\',\'".join([str(x.table_id) for x in orders if x.table_id is not None])
            tables_sector = {}
            for row in conn.select(self._GetTablesSector.format(order_ids)):
                tables_sector[row.get_entry(0)] = {"sector": row.get_entry(1), "source_table_id": row.get_entry(2)}

            return tables_sector

        return self.execute_with_connection(inner_func)

    _GetTablesSector = """
select distinct ts.tableid, coalesce(rt.sector, 'Comanda') as Sector, ts2.tableid as SourceTableId
from tableservice ts
left join (select tableid, sector from restauranttable) rt on rt.tableid = ts.tableid
left join (select tableid, serviceid from tableservice) ts2 on ts2.serviceid = ts.sourceserviceid
where ts.tableid in (select tableid from restauranttable)
or ts.tableid in ('{}')"""


class TableSalesAverageInfo(object):
    def __init__(self, total_tables=0, total_customers=0, table_time_average_milliseconds=0):
        self.total_tables = total_tables
        self.total_customers = total_customers
        self.table_time_average_milliseconds = table_time_average_milliseconds
