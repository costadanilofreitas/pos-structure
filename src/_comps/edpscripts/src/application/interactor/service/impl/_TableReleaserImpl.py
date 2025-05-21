from application.domain import TableService  # noqa
from application.interactor.service import TableReleaser


class TableReleaserImpl(TableReleaser):
    def __init__(self, table_service):
        # type: (TableService) -> None
        self.table_service = table_service

    def release_all(self, pos_id):
        tables = self.table_service.list_tables(pos_id)
        for table in tables:
            if pos_id == table.current_pos_id:
                self.table_service.store_service(pos_id, table.id)
