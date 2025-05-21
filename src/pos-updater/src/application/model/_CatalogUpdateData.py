from datetime import datetime


class CatalogUpdateData(object):
    def __init__(self,
                 update_id=None,
                 update_name=None,
                 obtained_date=None,
                 downloaded_date=None,
                 backup_date=None,
                 applied_date=None,
                 notified_date=None):
        # type: (int, str, datetime, datetime, datetime, datetime, datetime) -> None

        self.update_id = update_id
        self.update_name = update_name
        self.obtained_date = obtained_date
        self.downloaded_date = downloaded_date
        self.backup_date = backup_date
        self.applied_date = applied_date
        self.notified_date = notified_date
