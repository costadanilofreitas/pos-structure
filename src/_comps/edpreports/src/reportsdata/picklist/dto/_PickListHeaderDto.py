from typing import Optional  # noqa
import datetime  # noqa


class PickListHeaderDto(object):
    def __init__(self, date, order_id, store, client_name):
        # type: (datetime, int, unicode, Optional[unicode]) -> ()
        self.date = date
        self.order_id = order_id
        self.store = store
        self.client_name = client_name
