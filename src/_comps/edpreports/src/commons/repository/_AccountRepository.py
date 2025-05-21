from datetime import datetime

from helper import BaseRepository, convert_from_utf_to_localtime
from persistence import Connection  # noqa
from typing import Optional, List  # noqa

from reports_app.cashtransferreport.dto import Transfer


class AccountRepository(BaseRepository):
    def __init__(self, mbcontext):
        super(AccountRepository, self).__init__(mbcontext)

    def get_transfers_by_business_period(self, initial_date, end_date, operator_id, report_pos, report_name):
        # type: (datetime, datetime, Optional[str], Optional[str], Optional[str]) -> List[Transfer]
        return self._get_transfer(initial_date, end_date, operator_id, report_pos, report_name)

    def get_transfers_by_real_date(self, initial_date, end_date, operator_id, report_pos, report_name):
        # type: (datetime, datetime, Optional[str], Optional[str], Optional[str]) -> List[Transfer]
        return self._get_transfer(initial_date, end_date, operator_id, report_pos, report_name)

    def get_transfers_by_session_id(self, session_id, report_name):
        # type: (unicode) -> List[Transfer]
        return self._get_transfer(None, None, None, session_id, report_name)

    def _get_transfer(self, initial_date, end_date, operator_id, report_pos, report_name):
        # type: (unicode, Optional[datetime], Optional[datetime], Optional[int], Optional[str], Optional[str]) -> List[Transfer]
        def inner_func(conn):
            # type: (Connection) -> List[Transfer]
            query = self._get_transfer_query(initial_date, end_date, operator_id, report_pos, report_name, report_pos)
            query_result = conn.select(query)
            transfers = []

            for transfer in query_result:
                self.append_transfers_type(transfer, transfers, report_name)

            return transfers

        return self.execute_with_connection(inner_func)

    _TransfersByBusinessPeriod = "select Description, SessionId, Timestamp, Amount, Period, Type " \
                                 "from Transfer where Period >= '{0}' and Period <= '{1}'"

    _TransfersByRealDate = "select Type, Amount from Transfer where strftime('%Y-%m-%d', Timestamp, 'localtime') >= " \
                           "'{0}' and strftime('%Y-%m-%d', Timestamp, 'localtime') <= '{1}'"

    _TransfersBySessionId = "select Type, Amount from Transfer where SessionId = '{0}'"

    def _get_transfer_query(self, initial_date, end_date, operator_id, report_pos, report_name, session_id):
        # type: (unicode, Optional[datetime], Optional[datetime], Optional[int], Optional[str], Optional[str]) -> List[Transfer]
        query = ''
        if report_name == "report_by_business_period" or report_name == "cash_in" or report_name == "cash_out" or report_name == "report_by_xml":
            query += self._get_transfer_query_business_period(end_date, initial_date)
        if report_name == "report_by_real_date":
            query += self._get_transfer_query_real_date(end_date, initial_date)
        if report_name == "report_by_session_id":
            query += self._get_transfer_query_session_id(session_id)
        if report_name != "report_by_xml":
            query += self._get_transfer_query_operator_id(operator_id, report_name)
        query += self._get_transfer_query_report_pos(report_pos, report_name)
        query += self._get_transfer_query_cash_out_cash_in(report_name)
        query += " order by Timestamp asc;"
        return query

    def _get_transfer_query_session_id(self, session_id):
        query = self._TransfersBySessionId
        query = query.format(session_id)
        return query

    def _get_transfer_query_real_date(self, end_date, initial_date):
        query = self._TransfersByBusinessPeriod
        query = query.format(initial_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"))
        return query

    def _get_transfer_query_business_period(self, end_date, initial_date):
        query = self._TransfersByBusinessPeriod
        query = query.format(initial_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"))
        return query

    @staticmethod
    def _get_transfer_query_operator_id(operator_id, report_name):
        query = ''
        if operator_id is not None and report_name != 'report_by_session_id':
            query += " and SessionId like '%user={0},%'".format(operator_id)
        return query

    @staticmethod
    def _get_transfer_query_report_pos(report_pos, report_name):
        query = ''
        if report_pos is not None and report_name != 'report_by_session_id':
            query += " and SessionId like '%pos={0},%'".format(report_pos)
        return query

    @staticmethod
    def _get_transfer_query_cash_out_cash_in(report_name):
        query = ''
        if report_name == 'cash_out':
            query += " and Type = 4"
        elif report_name == 'cash_in':
            query += " and (Type = 1 or Type = 3)"
        else:  # cash_in and cash_out
            query += " and (Type = 1 or Type = 3 or Type = 4)"

        return query

    def append_transfers_type(self, transfer, transfers, report_name):
        transfer_type = self._get_transfer_type(transfer)
        transfer_operator = self._get_transfer_operator(transfer, report_name)
        transfer_date = self._get_transfer_date(transfer, report_name)
        if transfer_date is not None:
            transfer_date = convert_from_utf_to_localtime(transfer_date)
        transfer_value = self._get_transfer_value(transfer, report_name)
        transfer_cash_in_cash_out = self._get_transfer_cash_in_cash_out(transfer, report_name)
        transfers.append(Transfer(transfer_type, transfer_operator, transfer_date, transfer_value, transfer_cash_in_cash_out))

    @staticmethod
    def _get_transfer_type(transfer):
        transfer_type = None if transfer.get_entry(5) is None else int(transfer.get_entry(5))
        return AccountRepository._select_transfer_type(transfer, transfer_type)

    @staticmethod
    def _select_transfer_type(transfer, transfer_type):
        cash_in_by_login = 1
        cash_in_by_manager_menu = 3

        if transfer_type == cash_in_by_login:
            return '$LOGIN'
        else:
            transfer_description = str(transfer.get_entry(0))
            if '"type":' in transfer_description:
                description = transfer_description.split('"type":')[1].split(',')[0][2:-1]
                if transfer_type == cash_in_by_manager_menu:
                    description = description[:-1]
                return description
        return ''

    @staticmethod
    def _get_transfer_operator(transfer, report_name):
        if report_name != "report_by_session_id":
            return str(transfer.get_entry(1).split("user=")[1].split(",")[0])
        return None

    @staticmethod
    def _get_transfer_date(transfer, report_name):
        if report_name != "report_by_session_id":
            return datetime.strptime(transfer.get_entry(2), "%Y-%m-%d %H:%M:%S")
        return None

    @staticmethod
    def _get_transfer_value(transfer, report_name):
        if report_name != "report_by_session_id":
            return float(transfer.get_entry(3))
        return float(transfer.get_entry(1))

    @staticmethod
    def _get_transfer_cash_in_cash_out(transfer, report_name):
        if report_name != "report_by_session_id":
            return int(transfer.get_entry(5))
        return int(transfer.get_entry(0))
