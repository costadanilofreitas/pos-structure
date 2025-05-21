class OrderProducedRequest(object):
    def __init__(self, remote_order_id, store_id, fiscal_xml, items, producing):
        # type: (str, str, str, str, bool) -> None

        self.remote_order_id = remote_order_id
        self.store_id = store_id
        self.fiscal_xml = fiscal_xml
        self.items = items
        self.producing = producing
