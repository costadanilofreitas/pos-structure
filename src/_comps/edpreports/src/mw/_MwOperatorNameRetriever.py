from domain import OperatorNameRetriever
from old_helper import BaseRepository
from persistence import Connection


class MwOperatorNameRetriever(OperatorNameRetriever, BaseRepository):
    def __init__(self, mbcontext):
        super(MwOperatorNameRetriever, self).__init__(mbcontext)

    def get_operator_name(self, operator_id):
        def inner_func(conn):
            # type: (Connection) -> str
            query = "select LongName from Users where UserId={}".format(operator_id)
            for line in conn.select(query):
                return line.get_entry(0).decode("utf-8")

        return self.execute_with_connection(inner_func)
