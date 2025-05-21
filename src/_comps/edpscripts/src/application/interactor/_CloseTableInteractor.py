from application.domain import TableService  # noqa


class CloseTableInteractor(object):
    def __init__(self, table_service):
        # type: (TableService) -> None
        self.table_service = table_service

    def execute(self, pos_id, table_id):
        # type: (str, str) -> str
        return self.table_service.close_table(pos_id, table_id)
