class OrderReadyToDeliveryRequest(object):
    def __init__(self, remote_order_id, produced_at, ready_to_delivery):
        # type: (str, str, str) -> None

        self.remote_order_id = remote_order_id
        self.produced_at = produced_at
        self.ready_to_delivery_at = ready_to_delivery
