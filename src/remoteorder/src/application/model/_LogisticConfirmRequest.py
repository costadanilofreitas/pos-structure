class LogisticConfirmRequest:
    def __init__(self, remote_order_id, adapter_name, adapter_logistic_id, is_delivery_by_store, courier_name):
        # type: (str, str, str, bool, str) -> None
        
        self.remote_order_id = remote_order_id
        self.adapter_name = adapter_name
        self.adapter_logistic_id = adapter_logistic_id
        self.is_delivery_by_store = is_delivery_by_store
        self.courier_name = courier_name
