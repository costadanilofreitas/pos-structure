class Table(object):
    def __init__(self, id="", current_pos_id="", status="", tab_id="", business_period=""):
        # type: (str, int, int, bool, int) -> None
        self.id = id
        self.current_pos_id = current_pos_id
        self.status = status
        self.tab_id = tab_id
        self.business_period = business_period
