# encoding: utf-8
from old_helper import BaseRepository


class ProductRepository(BaseRepository):

    def __init__(self, mbcontext):
        super(ProductRepository, self).__init__(mbcontext)

    def get_tenders_descripton(self):
        def inner_func(conn):
            query = self._TenderDescriptionQuery
            tenders = {}
            for x in conn.select(query):
                tenders[x.get_entry("TenderId")] = x.get_entry("TenderDescr")
            return tenders

        return self.execute_with_connection(inner_func)

    _TenderDescriptionQuery = """\
    SELECT t1.TenderId, t1.TenderDescr || ' ' || coalesce(t2.TenderDescr, '') AS TenderDescr
    FROM TenderType AS t1
    LEFt JOIN TenderType AS t2 ON t1.ParentTenderId = t2.TenderId
    """
