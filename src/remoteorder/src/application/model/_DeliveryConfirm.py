class DeliveryConfirm:
    def __init__(self, remote_order_id, adapter_logistic_id):
        # type: (str, str) -> None

        self.id = remote_order_id
        self.logistic_id = adapter_logistic_id
