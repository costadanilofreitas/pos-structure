from application.domain import TableService  # noqa


class SetTableAvailableInteractor(object):
    def __init__(self, table_service):
        # type: (TableService) -> None
        self.table_service = table_service

    def execute(self, pos_id, table_id):
        # type: (str, str) -> None
        self.table_service.set_table_available(pos_id, table_id)
