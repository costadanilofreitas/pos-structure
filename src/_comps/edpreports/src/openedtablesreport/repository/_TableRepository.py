# encoding: utf-8
from old_helper import BaseRepository


class TableRepository(BaseRepository):

    def __init__(self, mbcontext, pos_id):
        super(TableRepository, self).__init__(mbcontext)
        self.pos_id = pos_id

    def get_opened_tables(self):
        def inner_func(conn):
            query = self._TenderDescriptionQuery
            tables = []
            for x in conn.select(query):
                table_id = x.get_entry("TableId")

                if table_id not in tables:
                    tables.append(table_id)

            return tables

        return self.execute_with_connection(inner_func)

    _TenderDescriptionQuery = """\
    SELECT ts.TableId FROM TableService ts
    LEFT JOIN ServiceOrders so ON so.ServiceId = ts.ServiceId
    WHERE ts.FinishedTS IS NULL
    """