from unicodedata import normalize

from old_helper import BaseRepository
from persistence import Connection
from typing import List, Tuple


class TenderRepository(BaseRepository):
    def __init__(self, mbcontext):
        super(TenderRepository, self).__init__(mbcontext)

    def get_tender_names(self):
        # type: () -> List[Tuple[int, unicode]]
        def inner_func(conn):
            # type: (Connection) -> List[Tuple[int, unicode]]
            return [(int(x.get_entry(0)), _remove_accents(x.get_entry(1).decode("utf-8")))
                    for x in conn.select(self._TenderNamesQuery)]

        return self.execute_with_connection(inner_func)

    _TenderNamesQuery = "select TenderId, TenderDescr from TenderType"


def _remove_accents(text):
    return normalize('NFKD', unicode(text)).encode('ASCII', 'ignore')