from domain import SessionRepository
from old_helper import BaseRepository
from persistence import Connection  # noqa


class MwSessionRepository(SessionRepository, BaseRepository):
    def __init__(self, mbcontext):
        super(MwSessionRepository, self).__init__(mbcontext)

    def get_unique_user_session_count(self, initial_date, end_date):
        def inner_func(conn):
            # type: (Connection) -> int
            query = "select count(1) from UserSession where BusinessPeriod >= '{0}' and BusinessPeriod <= '{1}'"\
                .format(initial_date.strftime("%Y%m%d"),
                        end_date.strftime("%Y%m%d"))
            for line in conn.select(query):
                return int(line.get_entry(0))

        return self.execute_with_connection(inner_func)
