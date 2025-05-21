class DeliveryEvent(object):
    def __init__(self, order_id, remote_order_id, event_type, event_data):
        # type: (int, str, str, str) -> None

        self.order_id = order_id
        self.remote_order_id = remote_order_id
        self.event_type = event_type
        self.event_data = event_data
