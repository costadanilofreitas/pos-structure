from helper import BaseRepository
from datetime import datetime
from persistence import Connection
from ..model import Transfer
from typing import Optional, List


class AccountRepository(BaseRepository):
    TypeRealDate = "RealDate"
    TypeBusinessPeriod = "BusinessPeriod"
    TypeSessionId = "SessionId"

    def __init__(self, mbcontext):
        super(AccountRepository, self).__init__(mbcontext)

    def get_transfers_by_real_date(self, initial_date, end_date, operator_id, report_pos):
        # type: (datetime, datetime, Optional[unicode]) -> List[Transfer]
        return self._get_transfer(self.TypeRealDate, initial_date, end_date, operator_id, None, report_pos)

    def get_transfers_by_business_period(self, initial_date, end_date, operator_id, report_pos):
        # type: (datetime, datetime, Optional[unicode]) -> List[Transfer]
        return self._get_transfer(self.TypeBusinessPeriod, initial_date, end_date, operator_id, None, report_pos)

    def get_transfers_by_session_id(self, session_id):
        # type: (unicode) -> List[Transfer]
        return self._get_transfer(self.TypeSessionId, None, None, None, session_id, None)

    def _get_transfer(self, report_type, initial_date, end_date, operator_id, session_id, report_pos):
        # type: (unicode, Optional[datetime], Optional[datetime], Optional[unicode], Optional[unicode], Optional[unicode]) -> List[Transfer]
        def inner_func(conn):
            # type: (Connection) -> List[Transfer]
            if report_type == self.TypeRealDate:
                query = self._TransfersByRealDate
                query = query.format(initial_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
            elif report_type == self.TypeBusinessPeriod:
                query = self._TransfersByBusinessPeriod
                query = query.format(initial_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"))
            else:
                query = self._TransfersBySessionId
                query = query.format(session_id)

            if operator_id is not None:
                query += " and SessionId like '%user={0},%'".format(operator_id)

            if report_pos is not None:
                query += " and PosId = {0}".format(report_pos)

            return [Transfer(int(x.get_entry(0)), float(x.get_entry(1))) for x in conn.select(query)]

        return self.execute_with_connection(inner_func)

    _TransfersByRealDate = "select Type, Amount from Transfer where strftime('%Y-%m-%d', Timestamp, 'localtime') >= '{0}' and strftime('%Y-%m-%d', Timestamp, 'localtime') <= '{1}'"

    _TransfersByBusinessPeriod = "select Type, Amount from Transfer where Period >= '{0}' and Period <= '{1}'"

    _TransfersBySessionId = "select Type, Amount from Transfer where SessionId = '{0}'"
