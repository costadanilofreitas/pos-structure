from application.domain import TableService  # noqa
from application.domain.ui import ScreenChanger, ScreenIdEnum  # noqa
from application.interactor.service import TableReleaser  # noqa


class StartServiceInteractor(object):
    def __init__(self, screen_changer, table_service, table_releaser):
        # type: (ScreenChanger, TableService, TableReleaser) -> None
        self.screen_changer = screen_changer
        self.table_service = table_service
        self.table_releaser = table_releaser

    def execute(self, pos_id, table_id="", seats="", with_order=False, tab_id=""):
        # type: (str, str, int, bool) -> str
        self.table_releaser.release_all(pos_id)
        ret = self.table_service.start_service(pos_id, table_id, seats, tab_id)
        if with_order:
            self.table_service.create_order(pos_id, table_id)
            self.screen_changer.change(pos_id, ScreenIdEnum.create_table_order)
            return "REDIRECT"

        return ret
