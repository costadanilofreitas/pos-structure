from datetime import datetime  # noqa


class LogoutSummaryInfo(object):
    def __init__(self, pos_id, store_id, operator_id, business_date, authorizer, login_time, session_id, query_date):
        # type: (int, int, int, unicode, float, unicode, unicode, unicode, unicode, datetime) -> ()
        self.pos_id = pos_id
        self.store_id = store_id
        self.operator_id = operator_id
        self.business_date = business_date
        self.authorizer = authorizer
        self.login_time = login_time
        self.session_id = session_id
        self.query_date = query_date
